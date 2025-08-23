import time
from collections import defaultdict, deque
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

import numpy as np
from granturismo.model.packet import Packet


class ProxyMode:
    ACCEL = "ACCEL"  # a
    SPEC_POWER = "SPEC_POWER"  # a * v
    DRAG_CORRECTED = "DRAG_CORRECTED"  # a + |a_drag(v)|


class CoastDownFitter:
    """
    Recursive least-squares fit for coast decel:
        a(v) ≈ -(C0 + C1*v + C2*v^2)

    Once `warm_samples` are collected, the model stops updating
    (parameters are frozen).
    """

    def __init__(self, warm_samples: int = 200, lam: float = 0.995):
        self.C0 = 0.0
        self.C1 = 0.0
        self.C2 = 0.0
        self.P = [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]]
        self.lam = lam
        self.samples = 0
        self.warm_samples = int(warm_samples)
        self._frozen = False  # new: freeze flag

    def warm(self) -> bool:
        return self._frozen

    def frozen(self) -> bool:
        """Return True if the fitter has stopped updating."""
        return self._frozen

    def update(self, v: float, a: float) -> None:
        if self._frozen:
            return  # Do nothing once frozen

        # y = -a, phi = [1, v, v^2]
        y = -float(a)
        phi = [1.0, float(v), float(v) * float(v)]
        th = [self.C0, self.C1, self.C2]

        # gain
        Pphi = [sum(self.P[i][j] * phi[j] for j in range(3)) for i in range(3)]
        denom = self.lam + sum(phi[i] * Pphi[i] for i in range(3))
        K = [p / denom for p in Pphi]

        # theta update
        yhat = sum(phi[i] * th[i] for i in range(3))
        err = y - yhat
        th = [th[i] + K[i] * err for i in range(3)]
        self.C0, self.C1, self.C2 = th

        # covariance update
        Kphi = [[K[i] * phi[j] for j in range(3)] for i in range(3)]
        Iminus = [
            [(1.0 if i == j else 0.0) - Kphi[i][j] for j in range(3)] for i in range(3)
        ]
        newP = [
            [sum(Iminus[i][k] * self.P[k][j] for k in range(3)) for j in range(3)]
            for i in range(3)
        ]
        self.P = [[newP[i][j] / self.lam for j in range(3)] for i in range(3)]

        self.samples += 1

        # Check if we've reached warm_samples -> freeze
        if self.samples >= self.warm_samples:
            self._frozen = True

    def predict(self, v: float) -> float:
        return -(self.C0 + self.C1 * v + self.C2 * v * v)

    def params(self) -> Tuple[float, float, float, int, int]:
        """Return (C0, C1, C2, N, warm_samples)."""
        return (
            self.C0,
            self.C1,
            self.C2,
            self.samples,
            self.warm_samples,
        )


@dataclass
class _BinStats:
    samples: deque
    maxlen: int = 200

    def add(self, val: float) -> None:
        self.samples.append(val)
        if len(self.samples) > self.maxlen:
            self.samples.popleft()

    def value(self) -> float:
        if not self.samples:
            return 0.0
        s = sorted(self.samples)
        k = int(0.95 * (len(s) - 1))  # 95th percentile for peak value
        return s[k]


class GearCurve:
    """Per-gear learned curve: 95th percentile of chosen proxy vs RPM."""

    def __init__(self) -> None:
        self.bins: Dict[int, _BinStats] = defaultdict(lambda: _BinStats(deque(), 200))
        self.curve_pts: List[Tuple[int, float]] = []

    @staticmethod
    def _bin(rpm: float) -> int:
        return int(rpm // 100) * 100

    def add(self, rpm: float, val: float) -> None:
        self.bins[self._bin(rpm)].add(val)

    def rebuild(self) -> None:
        pts = [
            (b, binstat.value()) for b, binstat in self.bins.items() if binstat.samples
        ]
        pts.sort()
        self.curve_pts = pts

    def value_at(self, rpm: float) -> float:
        if not self.curve_pts:
            return 0.0
        b = self._bin(rpm)
        bx, vx = min(self.curve_pts, key=lambda x: abs(x[0] - b))
        return vx


class ShiftECU:
    """
    ECU-side logic:
      - derive acceleration (EMA) if not provided,
      - fit coast-down model on clean coasts,
      - pick proxy (ACCEL/SPEC_POWER/DRAG_CORR),
      - learn per-gear curves,
      - compute shift crossover target.
    """

    def __init__(self, coast_warm_samples: int = 200):
        self._coast = CoastDownFitter(warm_samples=coast_warm_samples)
        self._gear_curves: Dict[int, GearCurve] = defaultdict(GearCurve)

        self._last_rebuild_ts = 0.0
        self._last_speed: Optional[float] = None
        self._a_ema: Optional[float] = 0.0
        self._alpha = 0.25  # EMA smoothing

        self.proxy_mode = ProxyMode.ACCEL
        self._coast_logged = False

    def coast_warm(self) -> bool:
        return self._coast.warm()

    def coast_params(self) -> Tuple[float, float, float, int, int]:
        return self._coast.params()

    def proxy_mode_name(self) -> str:
        return self.proxy_mode

    def measure_accel(self, v: float, dt: Optional[float]) -> Optional[float]:
        if dt and dt > 0 and self._last_speed:
            a_inst = (v - self._last_speed) / dt
            self._a_ema = (
                a_inst
                if self._a_ema is None
                else (self._alpha * a_inst + (1 - self._alpha) * self._a_ema)
            )
        self._last_speed = v
        return self._a_ema

    def ingest(self, pkt: Packet, dt: Optional[float]) -> None:
        rpm = float(getattr(pkt, "engine_rpm", 0.0) or 0.0)
        gear = int(getattr(pkt, "current_gear", 0) or 0)
        v = float(getattr(pkt, "car_speed", 0.0) or 0.0)
        throttle = float(getattr(pkt, "throttle", 0.0) or 0.0)
        brake = float(getattr(pkt, "brake", 0.0) or 0.0)

        a = self.measure_accel(v, dt)

        # Keep feeding coast model forever (even after warm) when coasting cleanly
        # FIXME: needed?
        if a is not None and throttle < 0.05 and brake < 0.05 and v > 5.0:
            self._coast.update(v, a)

        if not self._coast_logged and self._coast.warm():
            C0, C1, C2, N, thr = self._coast.params()
            print(
                f"[CoastDown] Model warm (N={int(N)}/{thr}). C0={C0:.5f}  C1={C1:.5f}  C2={C2:.7f}"
            )
            self._coast_logged = True

        # Choose proxy to learn
        proxy = None
        if a is not None:
            if self._coast.warm():
                proxy = a + abs(self._coast.predict(v))
                self.proxy_mode = ProxyMode.DRAG_CORRECTED
            else:
                if v > 1.0:
                    proxy = a * v
                    self.proxy_mode = ProxyMode.SPEC_POWER
                else:
                    proxy = a
                    self.proxy_mode = ProxyMode.ACCEL

        if rpm > 0 and gear > 0 and proxy is not None and proxy > 0:
            self._gear_curves[gear].add(rpm, proxy)

    def maybe_rebuild(self) -> None:
        now = time.monotonic()
        if now - self._last_rebuild_ts < 0.5:
            return
        self._last_rebuild_ts = now
        for gc in self._gear_curves.values():
            gc.rebuild()

    def get_shift_target(
        self, gear: int, ratios: List[float], redline: float
    ) -> Optional[float]:
        """
        Optimal shift from gear -> gear+1 when (at the *same vehicle speed*)
        the next gear produces more tractive effort (proxy) than the current gear.

        This version:
          - uses ONLY gear ratios (final drive cancels)
          - searches from the top end of the current gear to avoid low-RPM noise
          - returns the highest sensible crossover (with a small hysteresis)
        """
        g = self._gear_curves.get(gear)
        g1 = self._gear_curves.get(gear + 1)
        if not g or not g1 or not g.curve_pts or not g1.curve_pts:
            return None
        if gear >= len(ratios) - 1 or ratios[gear] <= 0 or ratios[gear + 1] <= 0:
            return None

        ratio, next_ratio = ratios[gear], ratios[gear + 1]
        # sort current-gear RPM samples
        rpms = sorted(b for (b, _) in g.curve_pts)
        if not rpms:
            return None

        # Only consider the upper portion of the RPM band to avoid early noisy crossings.
        # e.g. top 40% of sampled RPMs.
        start_idx = int(0.6 * (len(rpms) - 1))
        candidates = []

        for r in rpms[start_idx:]:
            # Same-vehicle-speed mapping between gears:
            # speed ~ rpm / overall_ratio; to keep speed equal:
            # r_next = r * (next_ratio / ratio)
            r_next = r * (next_ratio / ratio)

            # Stay within plausible evaluation range for the next gear
            if (
                r_next <= 0 or r_next > redline * 1.1
            ):  # allow tiny extrapolation headroom
                continue

            # Compare tractive effort proxies at same speed
            # (Your per-gear proxy is already wheel-force-like; final drive cancels.)
            if g1.value_at(r_next) > g.value_at(r):
                candidates.append(r)

        if not candidates:
            return None

        # Pick the LAST (highest RPM) crossing -> avoids short-shifting
        r_shift = candidates[-1]

        # Small hysteresis offset to avoid banging limiter after shift (empirical)
        r_shift_cmd = min(r_shift - 80.0, redline)
        # Ensure we don't command below the lowest sensible RPM observed for this gear
        lowest_observed = rpms[max(0, start_idx - 1)]
        r_shift_cmd = max(r_shift_cmd, lowest_observed)

        return r_shift_cmd if r_shift_cmd > 0 else None


class GearCurveModel:
    """
    Learns per-gear torque proxy curves from driving telemetry using
    RPM quantization and polynomial fitting.

    Instead of storing raw (rpm, torque_proxy) samples directly, this model
    discretizes the RPM band into fixed-size bins (e.g. every 250 RPM).
    For each gear, it maintains a dictionary mapping rpm_bin -> (sample_count, avg_torque).

    This reduces noise, ensures coverage across the full rev range, and allows
    for stable polynomial fitting once enough bins are filled.

    Workflow

    1. On each telemetry update, call `add_sample(gear, rpm, accel, speed)`:
       - RPM is quantized to the nearest bin.
       - Torque proxy is estimated as `accel x speed`.
       - The bin's running average torque is updated.

    2. Call `fit_curves()` (or `get_curves()`) to fit per-gear curves:
       - Fits a polynomial of degree `poly_degree` over the averaged bin values.
       - Computes R² as a measure of fit quality.
       - Returns a dict mapping gear -> (coeffs, x_min, x_max, r2, frozen).

    3. Curves can be “frozen” automatically when coverage exceeds 80% of
       the available RPM bins. This prevents later noisy samples from
       significantly altering a well-learned gear curve.

    Parameters

    max_rpm : int, default=10000
        The maximum RPM of the car (upper bound for binning).
    bin_size : int, default=250
        Size of RPM bins for quantization.
    poly_degree : int, default=3
        Degree of polynomial used to fit torque proxy curves.

    Attributes

    gear_bins : dict[int, dict[int, tuple[int, float]]]
        Per-gear dictionary storing {rpm_bin -> (sample_count, avg_torque)}.
    curves : dict[int, tuple]
        Per-gear fitted polynomial curves, stored as:
        (coeffs, x_min, x_max, r2, frozen).
    last_gear : int or None
        Tracks the most recent gear seen in telemetry.
    """

    def __init__(self, max_rpm: int = 10000, bin_size: int = 250, poly_degree: int = 3):
        self.max_rpm = max_rpm
        self.bin_size = bin_size
        self.poly_degree = poly_degree

        # per-gear -> dict[rpm_bin -> (count, avg_torque)]
        self.gear_bins: dict[int, dict[int, tuple[int, float]]] = defaultdict(dict)
        self.curves: dict[int, tuple] = {}  # gear -> (coeffs, x_min, x_max, r2, frozen)
        self.last_gear: int | None = None

    def _quantize_rpm(self, rpm: float) -> int:
        """Snap RPM to the nearest bin."""
        bin_idx = int(round(rpm / self.bin_size) * self.bin_size)
        return max(0, min(bin_idx, self.max_rpm))

    def add_sample(self, gear: int, rpm: float, accel: float, speed: float):
        if gear <= 0 or rpm <= 0:
            return
        torque_proxy = accel * speed
        rpm_bin = self._quantize_rpm(rpm)

        count, avg = self.gear_bins[gear].get(rpm_bin, (0, 0.0))
        # update average (running mean)
        new_avg = (avg * count + torque_proxy) / (count + 1)
        self.gear_bins[gear][rpm_bin] = (count + 1, new_avg)

        self.last_gear = gear

    def fit_curves(self):
        self.curves.clear()
        for gear, bins in self.gear_bins.items():
            if len(bins) < self.poly_degree + 1:
                continue

            xs = np.array(sorted(bins.keys()))
            ys = np.array([bins[rpm_bin][1] for rpm_bin in xs])

            x_min, x_max = xs.min(), xs.max()
            if x_max <= x_min:
                continue

            xs_norm = (xs - x_min) / (x_max - x_min)
            coeffs = np.polyfit(xs_norm, ys, deg=self.poly_degree)
            poly = np.poly1d(coeffs)
            y_pred = poly(xs_norm)

            ss_res = np.sum((ys - y_pred) ** 2)
            ss_tot = np.sum((ys - np.mean(ys)) ** 2)
            r2 = 1 - (ss_res / ss_tot if ss_tot > 0 else 0.0)

            # freeze curve if >80% bins filled
            coverage = len(bins) / (self.max_rpm / self.bin_size)
            frozen = coverage > 0.8

            self.curves[gear] = (coeffs, x_min, x_max, r2, frozen)

    def get_curves(self):
        self.fit_curves()
        return self.curves
