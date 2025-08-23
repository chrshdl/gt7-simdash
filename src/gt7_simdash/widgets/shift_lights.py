from __future__ import annotations

from typing import Any, List, Optional, Protocol, Tuple

from granturismo.model.packet import Packet

from ..core.ecu import ShiftECU
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
    """Shift-light widget (outer -> inward pairs, flash on target, ECU warmup pill)."""

    def __init__(
        self,
        anchor: Anchor,
        step_thresholds: Optional[List[float]] = None,
        color_thresholds: Tuple[float, float] = (0.5, 0.8),
        coast_warm_samples: int = 200,
    ) -> None:
        self._label = Label(
            text=" ",
            font=load_font(size=30, dir="digital", name=FontFamily.DIGITAL_7_MONO),
            color=Color.WHITE.rgb(),
            pos=(0, 0),
            center=True,
        )
        self._anchor = anchor

        # ECU brain
        self._ecu = ShiftECU(coast_warm_samples=coast_warm_samples)

        # LED device
        self._blinkt: BlinktIface = make_blinkt()
        try:
            self._blinkt.set_brightness(0.1)
        except Exception:
            pass
        self._blinkt.clear()
        self._blinkt.show()

        # Behavior
        self.step_thresholds = step_thresholds or [0.62, 0.78, 0.92, 0.985]
        self.color_thresholds = color_thresholds

        self._flash_timer = 0.0
        self._flash_on = False
        self._flashing = False
        self._last_target: Optional[float] = None
        self._last_gear = 0

    def enter(self) -> None:
        pass

    def exit(self) -> None:
        try:
            self._blinkt.clear()
            self._blinkt.show()
        except Exception:
            pass

    def handle_event(self, event: Any) -> bool:
        return False

    def update(self, model: Packet, dt: float | None = None) -> None:
        rpm = float(getattr(model, "engine_rpm", 0.0) or 0.0)
        gear = int(getattr(model, "current_gear", 0) or 0)
        ratios = list(getattr(model, "gear_ratios", [0, 3.2, 2.1, 1.6, 1.2, 1.0, 0.8]))
        if ratios and ratios[0] != 0.0:
            ratios = [0.0] + ratios
        redline = float(
            getattr(getattr(model, "rpm_alert", object()), "min", 7500.0) or 7500.0
        )

        # Reset flashing when gear changes
        if gear != self._last_gear:
            self._flashing = False
            self._flash_timer = 0.0
            self._flash_on = False
            self._last_gear = gear

        # ECU learning + target
        self._ecu.ingest(model, dt)
        self._ecu.maybe_rebuild()
        target = self._ecu.get_shift_target(gear, ratios, redline)
        if target is not None and target < 1200.0:
            target = None
        self._last_target = target

        # Hysteresis
        if target:
            if rpm >= target + SHIFT_HYST_RPM:
                self._flashing = True
            elif rpm <= target - SHIFT_HYST_RPM:
                self._flashing = False

        try:
            self._blinkt.clear()
            if rpm > 0 and gear > 0:
                if target and self._flashing:
                    self._flash_timer += dt or 1 / 60
                    if self._flash_timer >= FLASH_PERIOD_S:
                        self._flash_timer = 0.0
                        self._flash_on = not self._flash_on
                    self._flash_all_red(self._flash_on)
                else:
                    frac = rpm / (target if target else redline)
                    frac = max(0.0, min(1.0, frac))
                    self._set_progress_leds(frac)
            self._blinkt.show()
        except Exception:
            pass

        mode = self._ecu.proxy_mode_name()
        self._label.set_text(
            f"{int(rpm):04d} / {int(target):04d} [{mode}]"
            if target
            else f"{int(rpm):04d} [{mode}]"
        )

    def draw(self, surface: Any) -> None:
        w, h = surface.get_size()

        warm = self._ecu.coast_warm()
        C0, C1, C2, N, thr = self._ecu.coast_params()
        pill_text = f"COAST MODEL: {'ACTIVE' if warm else 'TRAINING'} ({N}/{thr})"
        self._draw_pill(
            surface,
            w - 330,
            h - 60,
            pill_text,
            Color.DARK_GREEN.rgb() if warm else Color.DEEP_PURPLE.rgb(),
        )

        if isinstance(self._blinkt, FakeBlinkt):
            margin = 320
            self._draw_led_bar(surface, margin, 16, w - 2 * margin, 30)

        # Anchor + label
        # TODO:
        # self._label.rect.center = self._anchor((w, h))
        # self._label.draw(surface)

    # --- helpers ----------------------------------------------------------------
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
