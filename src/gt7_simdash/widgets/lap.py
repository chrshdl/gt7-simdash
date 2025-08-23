from typing import Any, Callable, Optional, Tuple

import numpy as np
import pygame
from granturismo.model.packet import Packet
from scipy.spatial import cKDTree as KDTree

from ..core.utils import FontFamily, load_font
from ..widgets.base.colors import Color
from ..widgets.base.label import Label
from ..widgets.base.widget import Widget

Anchor = Callable[[Tuple[int, int]], Tuple[int, int]]  # (w, h) -> (cx, cy)


def _format_mmss_hh(seconds: float) -> str:
    """Format seconds as MM:SS.hh (hundredths)."""
    cs = max(0, int(seconds * 100 + 0.5))
    m = cs // 6000
    s = (cs // 100) % 60
    hh = cs % 100
    return f"{m:02d}:{s:02d}.{hh:02d}"


class EstimatedLap(Widget):
    """
    Lap-time / delta widget.

    - Lap 1 (no reference yet): shows elapsed lap time as MM:SS.hh (white).
    - Lap ≥ 2: shows delta vs nearest checkpoint from the best lap:
        * faster -> green, prefixed with "-" (e.g., "-0.18")
        * slower/equal -> red, no sign (e.g., "0.23")
    - Uses `dt`, samples track positions at a fixed Hz, and quantizes (x, z)
      to a grid to keep the KD-tree compact.
    """

    def __init__(
        self,
        anchor: Anchor,
        *,
        font_name: str = FontFamily.DIGITAL_7_MONO,
        font_size: int = 64,
        color_idle: Tuple[int, int, int] = None,
        color_faster: Tuple[int, int, int] = None,
        color_slower: Tuple[int, int, int] = None,
        sample_hz: float = 15.0,  # 10–20 Hz is ideal
        grid_m: float = 0.25,  # quantization cell size in meters
        kd_leafsize: int = 16,
        size: Tuple[int, int] | None = None,
        min_size: Tuple[int, int] | None = None,  # optional minimum (w,h) when auto
        padding: int = 10,
        show_border: bool = True,
        border_width: int = 2,
        border_padding: int = 0,
        border_radius: int = 4,
        border_color: Tuple[int, int, int] | None = Color.GREY.rgb(),
    ) -> None:
        super().__init__()
        self._anchor = anchor
        self._label = Label(
            text="--:--.--",
            font=load_font(size=font_size, dir="digital", name=font_name),
            color=(color_idle or Color.WHITE.rgb()),
            pos=(0, 0),
            center=True,
        )
        self._color_idle = color_idle or Color.WHITE.rgb()
        self._color_faster = color_faster or Color.GREEN.rgb()
        self._color_slower = color_slower or Color.RED.rgb()

        self._fixed_size = size
        self._min_size = min_size or (0, 0)
        self._padding = int(padding)
        self._box_size: Tuple[int, int] | None = None

        self._show_border = bool(show_border)
        self._border_w = int(border_width)
        self._border_pad = int(border_padding)
        self._border_r = int(border_radius)
        self._border_color = border_color

        # timing
        self._lap_index: int = -1
        self._lap_time_s: float = 0.0
        self._best_time_s: float = float("inf")

        # sampling
        self._sample_hz = max(1e-3, float(sample_hz))
        self._sample_interval = 1.0 / self._sample_hz
        self._sample_accum = 0.0
        self._grid = float(grid_m)

        self._tenths_last: float | None = None
        self._tenths_hold = 0.0
        self._tenths_debounce_s = 0.06  # must hold for 60 ms
        self._tenths_deadband_s = 0.004  # ~4 ms of deadband (was 8 ms)

        # current lap samples: {(qx, qz): time_s}
        self._track_positions: dict[Tuple[float, float], float] = {}

        # best lap reference (frozen at the moment a new best is achieved)
        self._best_pts_np = None  # Nx2 float32 (if numpy available)
        self._best_times_np = None  # N float32
        self._best_pts_list = None  # list[tuple[float,float]] (fallback)
        self._best_times_list = None  # list[float]
        self._kdtree = None  # cKDTree
        self._kd_leafsize = int(kd_leafsize)

    def enter(self) -> None:
        if self._fixed_size:
            self._box_size = tuple(map(int, self._fixed_size))
            return

        # Measuring widest text to be shown
        samples = ["88:88.88", "--:--.--", "-9.99"]
        old = getattr(self._label, "text", None)
        max_w = max_h = 0
        for s in samples:
            self._label.set_text(s)
            r = self._label.rect
            max_w = max(max_w, r.w)
            max_h = max(max_h, r.h)
        if old is not None:
            self._label.set_text(old)

        w = max_w + self._padding * 2
        h = max_h + self._padding * 2
        w = max(w, self._min_size[0])
        h = max(h, self._min_size[1])
        self._box_size = (int(w), int(h))

    def exit(self) -> None:
        pass

    def handle_event(self, event) -> bool:
        return False

    def update(self, packet: Packet, dt: float | None = None) -> None:
        """Advance timing & display delta/elapsed."""
        dt = float(dt or 0.0)

        flags = getattr(packet, "flags", None)
        paused = bool(getattr(flags, "paused", False))
        loading = bool(getattr(flags, "loading_or_processing", False))
        lap_count = int(getattr(packet, "lap_count", 0) or 0)

        # Reset if lap counter is 0 / invalid
        if lap_count == 0 or lap_count is None:
            self._reset()
            return

        # Lap boundary: finalize previous, start new
        if lap_count != self._lap_index:
            if self._lap_index > 0:
                prev_time = self._lap_time_s
                # If it's a new best, freeze checkpoints and build KD-tree
                if prev_time < self._best_time_s and self._track_positions:
                    self._best_time_s = prev_time
                    self._build_reference_from_current()
            # start new lap
            self._lap_index = lap_count
            self._lap_time_s = 0.0
            self._track_positions.clear()
            self._sample_accum = 0.0

        # accumulate running time (paused/loading => no time passes)
        if not paused and not loading and self._lap_index > 0:
            self._lap_time_s += dt

        # sample current position at fixed Hz, quantized
        self._sample_accum += dt
        if self._sample_accum >= self._sample_interval:
            self._sample_accum -= self._sample_interval
            pos = getattr(packet, "position", None)
            if pos is not None:
                qx, qz = self._quantize(pos.x, pos.z)
                # keep the earliest time for a given cell (better for NN matching)
                self._track_positions.setdefault((qx, qz), self._lap_time_s)

        # choose display mode
        if self._has_reference() and self._lap_index >= 2:
            # delta vs nearest best-lap checkpoint
            pos = getattr(packet, "position", None)
            if pos is not None:
                qx, qz = self._quantize(pos.x, pos.z)
                delta = self._delta_vs_best((qx, qz))
            else:
                delta = None

            if delta is None:
                # fallback: show elapsed
                self._label.set_text(_format_mmss_hh(self._lap_time_s))
                self._label.color = self._color_idle
            else:
                shown = self._round_tenths_stable(delta, dt)
                faster = shown < 0.0
                text = f"-{abs(shown):.1f}" if faster else f"{shown:.1f}"
                self._label.set_text(text)
                self._label.color = self._color_faster if faster else self._color_slower
        else:
            # show elapsed time until we have a best reference
            self._label.set_text(_format_mmss_hh(self._lap_time_s))
            self._label.color = self._color_idle

    def get_size(self) -> Tuple[int, int]:
        if self._box_size is None:
            self.enter()
        return self._box_size or (0, 0)

    def draw(self, surface: Any) -> None:
        if self._box_size is None:
            self.enter()  # ensure size exists

        w, h = surface.get_size()
        cx, cy = self._anchor((w, h))

        box_w, box_h = self._box_size
        box = pygame.Rect(0, 0, box_w, box_h)
        box.center = (cx, cy)

        # center the label inside the fixed box
        # self._label.rect.center = box.center
        self._label.rect.centerx = box.centerx
        self._label.rect.bottom = box.bottom - self._padding

        # draw fixed border
        if self._show_border and self._border_w > 0:
            c = self._border_color or self._label.color
            pygame.draw.rect(
                surface, c, box, width=self._border_w, border_radius=self._border_r
            )

        # draw text
        self._label.draw(surface)

    def _set_text_color(self, text: str, color: Tuple[int, int, int]) -> None:
        self._label.color = color
        self._label.set_text(text)

    # def _smooth(self, x: Optional[float], dt: float) -> Optional[float]:
    #     if x is None:
    #         self._delta_ema = None
    #         return None
    #     if self._delta_ema is None:
    #         self._delta_ema = float(x)
    #         return self._delta_ema
    #     alpha = 1.0 - math.exp(-dt / max(1e-3, self._smooth_tau))
    #     self._delta_ema += (x - self._delta_ema) * alpha
    #     return self._delta_ema

    # def _quantize_stable(self, x: float) -> float:
    #     # snap to hundredths, but hold previous if inside a small deadband
    #     q = round(x * 100.0) / 100.0
    #     if self._display_delta is None:
    #         self._display_delta = q
    #         return q
    #     if abs(x - self._display_delta) < self._hysteresis:
    #         return self._display_delta
    #     self._display_delta = q
    #     return q

    def _round_tenths_stable(self, x: float, dt: float) -> float:
        q = round(x * 10.0) / 10.0
        if self._tenths_last is None:
            self._tenths_last = q
            self._tenths_hold = 0.0
            return q
        # if within small deadband of current shown value, don’t change
        if abs(x - self._tenths_last) < self._tenths_deadband_s:
            self._tenths_hold = 0.0
            return self._tenths_last
        # if rounded digit hasn’t actually changed, keep current
        if q == self._tenths_last:
            self._tenths_hold = 0.0
            return self._tenths_last
        # different tenth -> require brief hold before committing
        self._tenths_hold += dt
        if self._tenths_hold < self._tenths_debounce_s:
            return self._tenths_last
        self._tenths_last = q
        self._tenths_hold = 0.0
        return self._tenths_last

    def _quantize(self, x: float, z: float) -> Tuple[float, float]:
        """Quantize world coords to a grid to reduce noise and KD size."""
        g = self._grid
        return (round(float(x) / g) * g, round(float(z) / g) * g)

    def _has_reference(self) -> bool:
        return (
            (self._kdtree is not None)
            or (self._best_pts_np is not None and self._best_times_np is not None)
            or (self._best_pts_list is not None and self._best_times_list is not None)
        )

    def _build_reference_from_current(self) -> None:
        """Freeze current lap samples as the new best and build KD-tree."""
        points = list(self._track_positions.keys())
        times = list(self._track_positions.values())
        if not points:
            return

        pts_np = np.asarray(points, dtype=np.float32)  # (N, 2)
        t_np = np.asarray(times, dtype=np.float32)  # (N,)
        self._best_pts_np = pts_np
        self._best_times_np = t_np
        self._best_pts_list = None
        self._best_times_list = None

        # Build KD-tree
        if self._best_pts_np is not None:
            self._kdtree = KDTree(self._best_pts_np, leafsize=self._kd_leafsize)

    def _delta_vs_best(self, qpos: Tuple[float, float]) -> Optional[float]:
        """Return current_lap_time - best_time_at_nearest_checkpoint."""
        if (
            self._kdtree is not None
            and self._best_pts_np is not None
            and self._best_times_np is not None
        ):
            # SciPy supports workers=-1 in newer versions; guard it
            try:
                dist, idx = self._kdtree.query(qpos, k=1, workers=-1)
            except TypeError:
                dist, idx = self._kdtree.query(qpos, k=1)
            ref_time = float(self._best_times_np[int(idx)])
            return float(self._lap_time_s - ref_time)

    def _reset(self) -> None:
        self._set_text_color("--:--.--", self._color_idle)
        self._lap_index = -1
        self._lap_time_s = 0.0
        self._best_time_s = float("inf")
        self._track_positions.clear()
        self._sample_accum = 0.0
        self._best_pts_np = None
        self._best_times_np = None
        self._best_pts_list = None
        self._best_times_list = None
        self._kdtree = None
