import json
import os
import time
from collections import deque
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

# ECU learns a per-car torque curve (relative scale) from WOT acceleration
# and computes optimal shift RPMs. It also buffers recent samples per gear
# for plotting, and exposes debug counters so you can see why learning may
# be gated.


@dataclass
class DynoCurve:
    rpm_min: float = 800.0
    rpm_max: float = 12000.0
    bin_size: float = 100.0
    torque_bins: List[float] = field(default_factory=list)
    counts: List[int] = field(default_factory=list)
    last_updated: float = field(default_factory=time.time)

    def __post_init__(self) -> None:
        if not self.torque_bins:
            n = int((self.rpm_max - self.rpm_min) / self.bin_size) + 1
            self.torque_bins = [0.0] * n
            self.counts = [0] * n

    @property
    def rpm_bins(self) -> List[float]:
        return [self.rpm_min + i * self.bin_size for i in range(len(self.torque_bins))]

    def idx(self, rpm: float) -> Optional[int]:
        if rpm < self.rpm_min or rpm > self.rpm_max:
            return None
        i = int((rpm - self.rpm_min) / self.bin_size)
        if 0 <= i < len(self.torque_bins):
            return i
        return None

    def add_sample(self, rpm: float, torque_proxy: float, alpha: float = 0.12) -> None:
        i = self.idx(rpm)
        if i is None:
            return
        if self.counts[i] > 12:
            mean = self.torque_bins[i]
            if torque_proxy > 3.5 * max(mean, 1e-6):
                return
        old = self.torque_bins[i]
        new = old * (1.0 - alpha) + alpha * max(0.0, torque_proxy)
        self.torque_bins[i] = new
        self.counts[i] += 1
        self.last_updated = time.time()

    def smoothed(self) -> Tuple[List[float], List[float]]:
        y = self.torque_bins[:]
        n = len(y)
        if n < 3:
            return self.rpm_bins, y
        sm = [0.0] * n
        for i in range(n):
            acc = y[i]
            k = 1
            if i > 0:
                acc += y[i - 1]
                k += 1
            if i + 1 < n:
                acc += y[i + 1]
                k += 1
            sm[i] = acc / k
        return self.rpm_bins, sm

    def coverage(self) -> float:
        have = sum(1 for c in self.counts if c >= 3)
        return have / max(1, len(self.counts))

    def torque_at(self, rpm: float) -> float:
        xs, ys = self.smoothed()
        if not xs:
            return 0.0
        if rpm <= xs[0]:
            return ys[0]
        if rpm >= xs[-1]:
            return ys[-1]
        lo, hi = 0, len(xs) - 1
        while lo + 1 < hi:
            mid = (lo + hi) // 2
            if xs[mid] <= rpm:
                lo = mid
            else:
                hi = mid
        x0, x1 = xs[lo], xs[hi]
        y0 = ys[lo]
        y1 = ys[hi]
        t = (rpm - x0) / max(1e-6, (x1 - x0))
        return y0 * (1 - t) + y1 * t


@dataclass
class CarModel:
    car_id: int
    curve: DynoCurve = field(default_factory=DynoCurve)
    gear_ratios: List[float] = field(default_factory=list)
    redline_rpm: float = 7500.0
    idle_rpm: float = 800.0
    shift_up_rpm: Dict[int, float] = field(default_factory=dict)
    shift_down_rpm: Dict[int, float] = field(default_factory=dict)
    recent_by_gear: Dict[int, deque] = field(default_factory=dict)


class ECU:
    def __init__(self, storage_dir: str | None = None) -> None:
        self.storage_dir = os.path.expanduser(storage_dir or "~/.gt7_ecu")
        os.makedirs(self.storage_dir, exist_ok=True)
        self.models: Dict[int, CarModel] = {}
        self._prev_speed: Optional[float] = None
        self._accel_lp: float = 0.0
        self._last_car_id: Optional[int] = None
        self._last_save: float = 0.0
        self._dbg = {
            "ok": 0,
            "bad_gear": 0,
            "rpm_gate": 0,
            "throttle": 0,
            "brake": 0,
            "clutch": 0,
            "accel": 0,
            "speed": 0,
        }
        self._last_throttle_raw: float = 0.0
        self._last_throttle: float = 0.0  # normalized 0..1
        self._last_speed: float = 0.0  # m/s
        self._thr_seen_max: float = 1.0  # for dynamic scaling fallback

    # --- Public ------------------------------------------------------------
    def update(self, pkt, dt: Optional[float]) -> None:
        car_id = int(getattr(pkt, "car_id", 0) or 0)
        model = self._get_or_load_model(car_id)

        # Redline hint only from rpm_alert.max
        rpm_alert = getattr(pkt, "rpm_alert", None)
        if rpm_alert is not None:
            mx = getattr(rpm_alert, "max", None)
            if isinstance(mx, (int, float)) and mx > 2000:
                model.redline_rpm = float(mx)
        # keep idle sane
        model.idle_rpm = max(600.0, min(model.idle_rpm, 1400.0))

        # Gear ratios
        gr = list(getattr(pkt, "gear_ratios", []) or [])
        if gr and (not model.gear_ratios or len(model.gear_ratios) != len(gr)):
            model.gear_ratios = gr

        # Speed estimate (prefer wheel RPS, else car_speed with km/h fix)
        wheel_radius = self._avg_wheel_radius(pkt) or 0.31
        v = self._estimate_speed(pkt, wheel_radius)
        self._last_speed = v

        a_raw = 0.0
        if dt and dt > 1e-3 and self._prev_speed is not None:
            a_raw = (v - self._prev_speed) / dt
        self._prev_speed = v
        tau = 0.20
        alpha = (dt / (tau + dt)) if dt else 0.15
        self._accel_lp = (1 - alpha) * self._accel_lp + alpha * a_raw

        rpm = float(getattr(pkt, "engine_rpm", 0.0) or 0.0)
        gear = int(getattr(pkt, "current_gear", 0) or 0)
        thr_raw = float(getattr(pkt, "throttle", 0.0) or 0.0)
        throttle = self._normalize_throttle(thr_raw)
        brake = float(getattr(pkt, "brake", 0.0) or 0.0)
        clutch = float(getattr(pkt, "clutch", 0.0) or 0.0)  # 0 = engaged, 1 = pressed

        self._last_throttle_raw = thr_raw
        self._last_throttle = throttle

        # GT7 gear numbers are 1..N; map to ratios idx 0..N-1
        ratio_idx = gear - 1
        valid_gear = (
            (gear >= 1) and (ratio_idx >= 0) and (ratio_idx < len(model.gear_ratios))
        )
        if not valid_gear:
            self._dbg["bad_gear"] += 1
            return

        if rpm < 1200.0:
            self._dbg["rpm_gate"] += 1
            return
        if throttle < 0.85:
            self._dbg["throttle"] += 1
            return
        if brake > 0.02:
            self._dbg["brake"] += 1
            return
        if clutch > 0.05:
            self._dbg["clutch"] += 1
            return
        if v < 1.0:
            self._dbg["speed"] += 1
            return
        if self._accel_lp <= 0.0:
            self._dbg["accel"] += 1
            return

        # Accept sample: torque proxy ~ a * R / G
        gear_ratio = model.gear_ratios[ratio_idx]
        torque_proxy = self._accel_lp * wheel_radius / max(1e-6, gear_ratio)
        torque_proxy = max(0.0, min(torque_proxy, 50.0))
        model.curve.add_sample(rpm, torque_proxy)
        self._push_recent(model, gear, rpm, torque_proxy)
        self._dbg["ok"] += 1

        # Recompute targets occasionally
        i = model.curve.idx(rpm) or 0
        if (model.curve.counts[i] % 8) == 0:
            self._recompute_targets(model)

        # Autosave
        now = time.time()
        if now - self._last_save > 7.0:
            self.save_if_needed()
            self._last_save = now

    def get_shift_targets(
        self, pkt
    ) -> Tuple[Optional[float], Optional[float], Dict[str, float]]:
        car_id = int(getattr(pkt, "car_id", 0) or 0)
        model = self._get_or_load_model(car_id)
        gear = int(getattr(pkt, "current_gear", 0) or 0)
        rpm = float(getattr(pkt, "engine_rpm", 0.0) or 0.0)
        up = model.shift_up_rpm.get(gear)
        dn = model.shift_down_rpm.get(gear)
        info = {
            "coverage": model.curve.coverage(),
            "redline": model.redline_rpm,
            "gear": float(gear),
            "rpm": rpm,
            "thr_raw": self._last_throttle_raw,
            "thr": self._last_throttle,
            "speed": self._last_speed,
            "dbg": (
                f"ok:{self._dbg['ok']} badg:{self._dbg['bad_gear']} rpm:{self._dbg['rpm_gate']} "
                f"Th:{self._dbg['throttle']} Br:{self._dbg['brake']} Cl:{self._dbg['clutch']} "
                f"a:{self._dbg['accel']} v:{self._dbg['speed']}"
            ),
        }
        return up, dn, info

    def progress_fraction(self, rpm: float, target_up_rpm: Optional[float]) -> float:
        if target_up_rpm and target_up_rpm > 0:
            return max(0.0, min(1.2, rpm / target_up_rpm))
        return 0.0

    def get_plot_data(
        self, pkt, gear: int
    ) -> Tuple[
        List[Tuple[float, float, float]],
        Tuple[float, float, float],
        List[Tuple[float, float]],
    ]:
        car_id = int(getattr(pkt, "car_id", 0) or 0)
        model = self._get_or_load_model(car_id)
        dq = model.recent_by_gear.get(int(gear))
        now = time.time()
        pts: List[Tuple[float, float, float]] = []
        if dq is not None:
            pts = [(r, p, max(0.0, now - ts)) for (r, p, ts) in list(dq)]
        xs, ys = model.curve.smoothed()
        y_max = 0.0
        if ys:
            y_max = max(y_max, max(ys))
        if pts:
            y_max = max(y_max, max(p for _, p, _ in pts))
        if y_max <= 1e-6:
            y_max = 1.0
        curve = list(zip(xs, ys)) if xs and ys else []
        return pts, (model.curve.rpm_min, model.curve.rpm_max, y_max), curve

    def save_if_needed(self) -> None:
        for cm in self.models.values():
            # save every 15 seconds
            if time.time() - cm.curve.last_updated < 15.0:
                self._save_model(cm)

    # --- Internals ---------------------------------------------------------
    def _normalize_throttle(self, t: float) -> float:
        # Normalize throttle from common telemetry ranges to [0,1].
        if t <= 1.2:
            return max(0.0, min(1.0, t))
        # 0..100 scale
        if 0.0 <= t <= 110.0:
            return max(0.0, min(1.0, t / 100.0))
        # 0..255 scale
        if 0.0 <= t <= 260.0:
            return max(0.0, min(1.0, t / 255.0))
        # Fallback: dynamic max tracking
        self._thr_seen_max = max(self._thr_seen_max, t)
        return max(0.0, min(1.0, t / max(1.0, self._thr_seen_max)))

    def _get_or_load_model(self, car_id: int) -> CarModel:
        if car_id not in self.models:
            cm = self._load_model(car_id)
            self.models[car_id] = cm
            self._last_car_id = car_id
        return self.models[car_id]

    def _avg_wheel_radius(self, pkt) -> Optional[float]:
        wheels = getattr(pkt, "wheels", None)
        if not wheels:
            return None
        radii = []
        try:
            for w in wheels:
                r = float(getattr(w, "radius", 0.0) or 0.0)
                if r > 0:
                    radii.append(r)
        except TypeError:
            for name in ("front_left", "front_right", "rear_left", "rear_right"):
                w = getattr(wheels, name, None)
                if w is not None:
                    r = float(getattr(w, "radius", 0.0) or 0.0)
                    if r > 0:
                        radii.append(r)
        if not radii:
            return None
        return sum(radii) / len(radii)

    def _estimate_speed(self, pkt, wheel_radius: float) -> float:
        # """Return vehicle speed in m/s.
        # Prefer wheel RPS; if it's tiny, fall back to wheel ground_speed; then car_speed.
        # Convert car_speed from km/h when needed.
        # """
        # wheels = getattr(pkt, "wheels", None)
        # # 1) Prefer RPS if sensible
        # rps_vals = []
        # try:
        #     rps_vals = [float(getattr(w, "rps", 0.0) or 0.0) for w in (wheels or [])]
        # except TypeError:
        #     for name in ("front_left", "front_right", "rear_left", "rear_right"):
        #         w = getattr(wheels, name, None)
        #         if w is not None:
        #             rps_vals.append(float(getattr(w, "rps", 0.0) or 0.0))
        # if rps_vals:
        #     avg_rps = sum(rps_vals) / len(rps_vals)
        #     if avg_rps > 0.2:  # ~ >1.25 m/s with 0.31 m radius
        #         return 2.0 * math.pi * avg_rps * wheel_radius

        # # 2) Try wheel ground_speed (already m/s in schema)
        # gs = []
        # try:
        #     gs = [float(getattr(w, "ground_speed", 0.0) or 0.0) for w in (wheels or [])]
        # except TypeError:
        #     for name in ("front_left", "front_right", "rear_left", "rear_right"):
        #         w = getattr(wheels, name, None)
        #         if w is not None:
        #             gs.append(float(getattr(w, "ground_speed", 0.0) or 0.0))
        # if gs:
        #     avg_gs = sum(gs) / len(gs)
        #     if abs(avg_gs) > 0.5:
        #         return avg_gs

        # 3) Fallback: car_speed in m/s
        v = float(getattr(pkt, "car_speed", 0.0))
        return v

    def _push_recent(
        self, model: CarModel, gear: int, rpm: float, proxy: float
    ) -> None:
        dq = model.recent_by_gear.get(gear)
        if dq is None:
            dq = deque(maxlen=500)
            model.recent_by_gear[gear] = dq
        dq.append((float(rpm), float(proxy), time.time()))

    def _recompute_targets(self, model: CarModel) -> None:
        gr = model.gear_ratios
        if not gr:
            return
        xs, ys = model.curve.smoothed()
        if sum(1 for c in model.curve.counts if c >= 3) < 8:
            return
        for g in range(1, len(gr)):
            Gg = gr[g - 1]
            Gn = gr[g] if g < len(gr) else None
            if Gn is None or Gg <= 0 or Gn <= 0:
                continue
            best_rpm = None
            for rpm in xs:
                if rpm < 1200.0:
                    continue
                if rpm > model.redline_rpm:
                    break
                t_curr = model.curve.torque_at(rpm) * Gg
                rpm_next = rpm * (Gn / Gg)
                t_next = model.curve.torque_at(rpm_next) * Gn
                if t_next >= t_curr:
                    best_rpm = rpm
                    break
            if best_rpm is None:
                best_rpm = min(model.redline_rpm, xs[-1] if xs else model.redline_rpm)
            model.shift_up_rpm[g] = best_rpm
        # Downshift hints for gears 2..N-1
        for g in range(2, len(gr)):
            Gg = gr[g - 1]
            Gd = gr[g - 2]
            if Gg <= 0 or Gd <= 0:
                continue
            best_rpm = None
            for rpm in xs:
                if rpm < 1000.0:
                    continue
                t_curr = model.curve.torque_at(rpm) * Gg
                rpm_low = rpm * (Gd / Gg)
                t_low = model.curve.torque_at(rpm_low) * Gd
                if t_curr >= t_low:
                    best_rpm = rpm
                    break
            if best_rpm is None:
                best_rpm = 1400.0
            model.shift_down_rpm[g] = best_rpm

    # --- Persistence -------------------------------------------------------
    def _model_path(self, car_id: int) -> str:
        return os.path.join(self.storage_dir, f"dyno_{car_id}.json")

    def _load_model(self, car_id: int) -> CarModel:
        path = self._model_path(car_id)
        if os.path.isfile(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                curve = DynoCurve(
                    rpm_min=data.get("rpm_min", 800.0),
                    rpm_max=data.get("rpm_max", 12000.0),
                    bin_size=data.get("bin_size", 100.0),
                    torque_bins=data.get("torque_bins", []),
                    counts=data.get("counts", []),
                )
                cm = CarModel(
                    car_id=car_id,
                    curve=curve,
                    gear_ratios=data.get("gear_ratios", []),
                    redline_rpm=data.get("redline_rpm", 7500.0),
                    idle_rpm=data.get("idle_rpm", 800.0),
                    shift_up_rpm={
                        int(k): float(v)
                        for k, v in data.get("shift_up_rpm", {}).items()
                    },
                    shift_down_rpm={
                        int(k): float(v)
                        for k, v in data.get("shift_down_rpm", {}).items()
                    },
                )
                return cm
            except Exception:
                pass
        return CarModel(car_id=car_id)

    def _save_model(self, cm: CarModel) -> None:
        try:
            path = self._model_path(cm.car_id)
            tmp = path + ".tmp"
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(
                    {
                        "rpm_min": cm.curve.rpm_min,
                        "rpm_max": cm.curve.rpm_max,
                        "bin_size": cm.curve.bin_size,
                        "torque_bins": cm.curve.torque_bins,
                        "counts": cm.curve.counts,
                        "gear_ratios": cm.gear_ratios,
                        "redline_rpm": cm.redline_rpm,
                        "idle_rpm": cm.idle_rpm,
                        "shift_up_rpm": cm.shift_up_rpm,
                        "shift_down_rpm": cm.shift_down_rpm,
                        "saved_at": time.time(),
                    },
                    f,
                    indent=2,
                )
            os.replace(tmp, path)
            print("ECU model updated...")
        except Exception:
            pass
