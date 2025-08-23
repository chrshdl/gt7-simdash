from typing import Any

import numpy as np
import pygame
from granturismo.model.packet import Packet

from ..core.ecu import GearCurveModel, ShiftECU
from ..widgets.base.colors import Color
from ..widgets.base.widget import Anchor, Widget


class GearCurvesWidget(Widget):
    """
    Realtime visualization of learned per-gear torque proxy curves.

    This widget queries the GearCurveModel (ECU-side) and draws smooth
    polynomial approximations of torque vs RPM for each gear, including
    a text label showing the gear number.

    Parameters

    anchor : Anchor
        Function mapping (width, height) -> center coordinates for widget placement.
    ecu_model : GearCurveModel
        The ECU-side learner that accumulates telemetry and fits curves.
    rpm_max : int
        Maximum RPM for x-axis scaling.
    proxy_max : float
        Maximum torque proxy value for y-axis scaling.

    Visualization

    - X-axis : RPM
    - Y-axis : Torque proxy (a x v)
    - One colored curve per gear
    - Curves update in real-time as the model learns
    - Gear number label drawn at the rightmost end of each curve
    """

    def __init__(
        self,
        anchor: Anchor,
        ecu_model: GearCurveModel,
        ecu_core: ShiftECU,
        rpm_max: int = 10000,
        proxy_max: float = 50.0,
        show_only_current_curve: bool = True,
    ):
        self._anchor = anchor
        self._ecu = ecu_model
        self._ecu_core = ecu_core
        self._rpm_max = rpm_max
        self._proxy_max = proxy_max

        self._gear_colors = {
            1: Color.GREEN.rgb(),
            2: Color.LIGHT_RED.rgb(),
            3: Color.BLUE.rgb(),
            4: Color.PURPLE.rgb(),
            5: Color.DARK_GREEN.rgb(),
            6: Color.RED.rgb(),
            7: Color.GREY.rgb(),
        }

        self._font = pygame.font.SysFont("Arial", 16, bold=True)
        self._last_drawn_gear: int | None = None
        self._show_only_current_curve = show_only_current_curve

    def enter(self):
        pass

    def exit(self):
        pass

    def handle_event(self, event: Any) -> bool:
        return False

    def update(self, model: Packet, dt: float | None = None) -> None:
        """
        Collect necessary telemetry samples.
        """
        gear = getattr(model, "current_gear", 0)
        rpm = getattr(model, "engine_rpm", 0.0)
        speed = getattr(model, "car_speed", 0.0)
        accel = self._ecu_core.measure_accel(speed, dt)

        self._ecu.add_sample(gear, rpm, accel, speed)

    def draw(self, surface: Any) -> None:
        w, h = surface.get_size()
        cx, cy = self._anchor((w, h))

        width, height = w // 4, h // 4
        rect = pygame.Rect(cx - width * 2, cy - height * 2, width, height)
        pygame.draw.rect(surface, Color.BLACK.rgb(), rect, 1)

        current_gear = self._ecu.last_gear
        if current_gear is None:
            return

        # Draw scatter points ONLY for the current gear
        bins = self._ecu.gear_bins.get(current_gear, {})
        color = self._gear_colors.get(current_gear, Color.WHITE.rgb())
        for rpm_bin, (count, avg_proxy) in bins.items():
            if not np.isfinite(rpm_bin) or not np.isfinite(avg_proxy):
                continue
            x = rect.left + (rpm_bin / self._rpm_max) * rect.width
            y = rect.bottom - (avg_proxy / self._proxy_max) * rect.height
            pygame.draw.circle(surface, color, (int(x), int(y)), 4)

        # Draw fitted curves
        curves = self._ecu.get_curves()
        for gear, (coeffs, x_min, x_max, r2, frozen) in curves.items():
            # If flag is on, skip curves that are not the current gear
            if self._show_only_current_curve and gear != current_gear:
                continue

            color = self._gear_colors.get(gear, (255, 255, 255))
            xs_norm = np.linspace(0, 1, 200)
            xs = xs_norm * (x_max - x_min) + x_min
            ys = np.poly1d(coeffs)(xs_norm)

            points = []
            for rpm_val, proxy_val in zip(xs, ys):
                if not np.isfinite(rpm_val) or not np.isfinite(proxy_val):
                    continue
                x = rect.left + (rpm_val / self._rpm_max) * rect.width
                y = rect.bottom - (proxy_val / self._proxy_max) * rect.height
                points.append((int(x), int(y)))

            if len(points) > 1:
                pygame.draw.lines(surface, color, False, points, 2)
                end_x, end_y = points[-1]
                label_text = f"G={gear}, R²={r2:.2f}{'✔' if frozen else ''}"
                label = self._font.render(label_text, True, color)
                surface.blit(label, (end_x + 5, end_y - 10))
