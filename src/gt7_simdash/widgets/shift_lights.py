import math
from typing import Any, List, Optional, Protocol, Tuple

from granturismo.model.packet import Packet

from ..core.ecu import ECU
from ..core.utils import FontFamily, load_font
from ..widgets.base.colors import Color
from ..widgets.base.label import Label
from ..widgets.base.widget import Anchor, Widget

FLASH_PERIOD_S = 0.12
SHIFT_HYST_RPM = 120.0


class BlinktIface(Protocol):
    NUM_PIXELS: int

    def set_brightness(self, v: float) -> None: ...
    def clear(self) -> None: ...
    def set_pixel(self, i: int, r: int, g: int, b: int) -> None: ...
    def show(self) -> None: ...
    def pixels(self) -> List[Tuple[int, int, int]]: ...


try:
    import blinkt as _blinkt_hw  # type: ignore

    _HAVE_BLINKT = True
except Exception:
    _HAVE_BLINKT = False
    _blinkt_hw = None


class RealBlinkt:
    """Hardware blinkt wrapper (no readable pixel buffer)."""

    def __init__(self):
        self.NUM_PIXELS = getattr(_blinkt_hw, "NUM_PIXELS", 8)
        try:
            _blinkt_hw.set_brightness(0.1)
        except Exception:
            pass
        self.clear()
        self.show()

    def set_brightness(self, v: float) -> None:
        try:
            _blinkt_hw.set_brightness(v)
        except Exception:
            pass

    def clear(self) -> None:
        try:
            _blinkt_hw.clear()
        except Exception:
            pass

    def set_pixel(self, i: int, r: int, g: int, b: int) -> None:
        try:
            _blinkt_hw.set_pixel(i, r, g, b)
        except Exception:
            pass

    def show(self) -> None:
        try:
            _blinkt_hw.show()
        except Exception:
            pass

    def pixels(self) -> List[Tuple[int, int, int]]:
        return []  # hardware has no readable buffer


class FakeBlinkt:
    """Memory-backed blinkt used when hardware is not present."""

    def __init__(self, num: int = 8):
        self.NUM_PIXELS = num
        self._buf = [(0, 0, 0)] * num
        self._brightness = 0.1

    def set_brightness(self, v: float) -> None:
        self._brightness = v

    def clear(self) -> None:
        self._buf = [(0, 0, 0)] * self.NUM_PIXELS

    def set_pixel(self, i: int, r: int, g: int, b: int) -> None:
        if 0 <= i < self.NUM_PIXELS:
            self._buf[i] = (int(r), int(g), int(b))

    def show(self) -> None:
        pass

    def pixels(self) -> List[Tuple[int, int, int]]:
        return list(self._buf)


def make_blinkt() -> BlinktIface:
    return RealBlinkt() if _HAVE_BLINKT else FakeBlinkt(8)


class ShiftLights(Widget):
    """Shift-light widget with ECU learning, target flash, and live per-gear scatter plot."""

    def __init__(
        self,
        anchor: Anchor,
        step_thresholds: Optional[List[float]] = None,
        color_thresholds: Tuple[float, float] = (0.5, 0.8),
    ) -> None:
        self._label = Label(
            text=" ",
            font=load_font(size=30, dir="digital", name=FontFamily.DIGITAL_7_MONO),
            color=Color.WHITE.rgb(),
            pos=(0, 0),
            center=True,
        )
        self._anchor = anchor

        self._ecu = ECU()

        # LED device
        self._blinkt: BlinktIface = make_blinkt()
        try:
            self._blinkt.set_brightness(0.1)
        except Exception:
            pass
        self._blinkt.clear()
        self._blinkt.show()

        # Behavior
        self.step_thresholds = step_thresholds or [0.25, 0.45, 0.60, 0.72]  # 4 pairs
        self.color_thresholds = color_thresholds

        self._flash_timer = 0.0
        self._flash_on = False
        self._flashing = False

        # cache for drawing
        self._last_frac = 0.0
        self._ready = False
        self._up_target: Optional[float] = None
        self._down_target: Optional[float] = None
        self._rpm: float = 0.0
        self._gear: int = 0

        # plot data
        self._show_plot = True
        self._scatter_points: List[Tuple[float, float, float]] = []  # (rpm, proxy, age)
        self._plot_bounds: Tuple[float, float, float] = (800.0, 12000.0, 1.0)
        self._curve_series: List[Tuple[float, float]] = []

    def enter(self) -> None:
        pass

    def exit(self) -> None:
        try:
            self._blinkt.clear()
            self._blinkt.show()
        except Exception:
            pass

    def handle_event(self, event: Any) -> bool:
        # Toggle plot with 'p'
        try:
            import pygame

            if event.type == pygame.KEYDOWN and event.key == pygame.K_p:
                self._show_plot = not self._show_plot
                return True
        except Exception:
            pass
        return False

    def update(self, model: Packet, dt: float | None = None) -> None:
        # Update ECU learning/state
        self._ecu.update(model, dt)

        self._rpm = float(getattr(model, "engine_rpm", 0.0))
        self._gear = int(getattr(model, "current_gear", 0))
        up, dn, info = self._ecu.get_shift_targets(model)
        self._up_target = up
        self._down_target = dn
        self._ready = info.get("coverage", 0.0) >= 0.55

        # Progress vs upshift target
        frac = self._ecu.progress_fraction(self._rpm, self._up_target)
        self._last_frac = frac

        # Decide flashing (at/over target RPM)
        target = self._up_target or info.get("redline", 7500.0)
        if target and self._rpm >= target:
            self._flashing = True
        elif target and self._rpm <= (target - SHIFT_HYST_RPM):
            self._flashing = False

        # LED output
        if self._flashing:
            self._flash_timer += dt or 0.0
            if self._flash_timer >= FLASH_PERIOD_S:
                self._flash_on = not self._flash_on
                self._flash_timer = 0.0
            self._flash_all_red(self._flash_on)
        else:
            self._flash_timer = 0.0
            self._flash_on = False
            self._set_progress_leds(frac)
        try:
            self._blinkt.show()
        except Exception:
            pass

        # Screen label
        label_txt = self._format_label(info)
        self._label.set_text(label_txt)

        # Fetch live scatter for current gear
        self._scatter_points, self._plot_bounds, self._curve_series = (
            self._ecu.get_plot_data(model, self._gear)
        )

    def draw(self, surface: Any) -> None:
        # LED bar visualization (for when no hardware)
        self._draw_led_bar(surface, x=20, y=20, w=240, h=28)

        # ECU pill: shows learning/ready and target(s)
        pill = "READY" if self._ready else "LEARNING"
        bg = Color.DARK_GREEN.rgb() if self._ready else Color.DARK_YELLOW.rgb()
        self._draw_pill(surface, x=20, y=60, text=f"ECU {pill}", bg=bg)

        # Gear/RPM pill
        self._draw_pill(
            surface,
            x=20,
            y=95,
            text=f"G{self._gear}  {int(self._rpm)} rpm",
            bg=Color.DARK_GREY.rgb(),
        )

        # Targets pill
        up = int(self._up_target) if self._up_target else None
        dn = int(self._down_target) if self._down_target else None
        txt = []
        if up:
            txt.append(f"UP {up} rpm")
        if dn:
            txt.append(f"DN {dn} rpm")
        if txt:
            self._draw_pill(
                surface, x=20, y=130, text="  ".join(txt), bg=Color.DARK_GREY.rgb()
            )

        # Numeric progress (center label)
        try:
            pass
        except Exception:
            return
        rect = self._label.surface.get_rect()
        rect.center = (surface.get_width() // 2, 26)
        surface.blit(self._label.surface, rect)

        # Live scatter plot (per gear)
        if self._show_plot:
            W = surface.get_width()
            plot_w, plot_h = 360, 160
            x = W - plot_w - 20
            y = 50
            self._draw_scatter_plot(surface, x, y, plot_w, plot_h)

    def _set_progress_leds(self, frac: float) -> None:
        n = self._blinkt.NUM_PIXELS
        pairs = [
            (i, n - 1 - i) for i in range(n // 2)
        ]  # outer -> in (0,7),(1,6),(2,5),(3,4)
        k_pairs = sum(1 for t in self.step_thresholds if frac >= t)
        k_pairs = max(0, min(len(pairs), k_pairs))

        lit = set()
        for p in range(k_pairs):
            a, b = pairs[p]
            lit.add(a)
            lit.add(b)

        t_green, t_yellow = self.color_thresholds
        for idx, (a, b) in enumerate(pairs):
            if a in lit:
                idx_frac = (idx + 1) / len(pairs)
                if idx_frac < t_green:
                    color = Color.DARK_GREEN.rgb()
                elif idx_frac < t_yellow:
                    color = Color.DARK_YELLOW.rgb()
                else:
                    color = Color.LIGHT_RED.rgb()
                self._blinkt.set_pixel(a, *color)
                self._blinkt.set_pixel(b, *color)
            else:
                self._blinkt.set_pixel(a, 0, 0, 0)
                self._blinkt.set_pixel(b, 0, 0, 0)

    def _flash_all_red(self, on: bool) -> None:
        n = self._blinkt.NUM_PIXELS
        color = Color.RED.rgb() if on else (0, 0, 0)
        for i in range(n):
            self._blinkt.set_pixel(i, *color)

    def _draw_pill(
        self, surface: Any, x: int, y: int, text: str, bg: Tuple[int, int, int]
    ) -> None:
        try:
            import pygame
        except Exception:
            return
        font = pygame.font.SysFont("Consolas", 16, bold=True)
        pad = 10
        timg = font.render(text, True, (240, 240, 250))
        rect = timg.get_rect()
        rect.topleft = (x + pad, y + pad)
        box = pygame.Rect(x, y, rect.width + 2 * pad, rect.height + 2 * pad)
        pygame.draw.rect(surface, bg, box, border_radius=10)
        pygame.draw.rect(surface, Color.BLACK.rgb(), box, width=2, border_radius=10)
        surface.blit(timg, rect)

    def _draw_led_bar(self, surface: Any, x: int, y: int, w: int, h: int) -> None:
        try:
            import pygame
        except Exception:
            return
        px = self._blinkt.pixels()
        if not px:
            return
        n = len(px)
        slot_w = w / n
        for i, (r, g, b) in enumerate(px):
            rect = pygame.Rect(x + i * slot_w + 2, y + 2, slot_w - 4, h - 4)
            pygame.draw.rect(surface, Color.DARK_GREY.rgb(), rect, border_radius=8)
            inner = rect.inflate(-6, -10)
            color = (
                (max(r, 10), max(g, 10), max(b, 10)) if (r + g + b) > 0 else (8, 8, 10)
            )
            pygame.draw.rect(surface, color, inner, border_radius=8)

    def _draw_scatter_plot(self, surface: Any, x: int, y: int, w: int, h: int) -> None:
        try:
            import pygame
        except Exception:
            return
        # Frame
        box = pygame.Rect(x, y, w, h)
        pygame.draw.rect(surface, (22, 22, 28), box, border_radius=10)
        pygame.draw.rect(surface, Color.BLACK.rgb(), box, width=2, border_radius=10)

        # Axes (inside padding)
        pad = 12
        inner = box.inflate(-2 * pad, -2 * pad)
        pygame.draw.rect(surface, (30, 30, 38), inner, border_radius=8)

        rpm_min, rpm_max, y_max = self._plot_bounds
        xr = max(1.0, rpm_max - rpm_min)

        # Curve (learned)
        if self._curve_series:
            pts = []
            for r, t in self._curve_series:
                sx = (r - rpm_min) / xr
                sx = 0.0 if sx < 0 else (1.0 if sx > 1 else sx)
                sy = 1.0 - min(1.0, t / y_max)
                px = inner.left + int(sx * inner.width)
                py = inner.top + int(sy * inner.height)
                pts.append((px, py))
            if len(pts) >= 2:
                import pygame

                pygame.draw.lines(surface, (120, 180, 255), False, pts, 2)

        # Scatter for current gear (fade with age)
        if self._scatter_points:
            import pygame

            lay = pygame.Surface((inner.width, inner.height), pygame.SRCALPHA)
            for r, p, age in self._scatter_points[-400:]:
                sx = (r - rpm_min) / xr
                if sx < 0 or sx > 1:
                    continue
                sy = 1.0 - min(1.0, p / y_max)
                px = int(sx * inner.width)
                py = int(sy * inner.height)
                fade = max(0.25, min(1.0, math.exp(-age / 8.0)))  # ~8s half-life
                col = (
                    int(255 * fade),
                    int(220 * fade),
                    int(80 * fade),
                    int(200 * fade),
                )
                pygame.draw.circle(lay, col, (px, py), 2)
            surface.blit(lay, (inner.left, inner.top))

    def _format_label(self, info: dict) -> str:
        cov = info.get("coverage", 0.0)
        red = int(info.get("redline", 0.0) or 0)
        rpm = int(info.get("rpm", 0.0) or 0)
        g = int(info.get("gear", 0.0) or 0)
        thr_raw = info.get("thr_raw", 0.0)
        thr = info.get("thr", 0.0)
        spd = info.get("speed", 0.0)
        dbg = info.get("dbg", "")
        if self._up_target:
            tgt = int(self._up_target)
            return f"G{g} {rpm}/{tgt}  RL {red}  Th {thr:.2f} ({thr_raw:.0f})  v {spd:.1f} m/s  cov {int(100 * cov)}%  {dbg}"
        return f"G{g} {rpm}  RL {red}  Th {thr:.2f} ({thr_raw:.0f})  v {spd:.1f} m/s  cov {int(100 * cov)}%  {dbg}"
