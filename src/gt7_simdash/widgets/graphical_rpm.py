import math
from typing import Any

import pygame
from granturismo.model.packet import Packet

from ..core.utils import FontFamily, load_font
from ..widgets.base.colors import Color
from ..widgets.base.label import Label
from ..widgets.base.widget import Widget


class GraphicalRPM(Widget):
    def __init__(
        self,
        alert_min,
        alert_max,
        max_rpm=9000,
        redline_rpm=8000,
        width=260,
        height=28,
        font_name=None,
        min_px_per_tick=3,  # smallest visual width per minor tick
        major_factor=10,  # major tick every N minor ticks
    ) -> None:
        self._alert_min = int(alert_min)
        self._alert_max = int(alert_max)
        self._max_rpm = int(max_rpm)
        self._redline_rpm = int(redline_rpm)
        self._width = int(width)
        self.height = int(height)
        self.font_name = font_name or FontFamily.DIGITAL_7_MONO

        self.current_rpm = 0

        # adaptive tick params
        self._min_px_per_tick = max(1, int(min_px_per_tick))
        self._major_factor = max(2, int(major_factor))  # at least every 2 minor ticks

        self._tick_step_rpm = 100  # minor tick RPM step (adaptive)
        self._major_step_rpm = 1000  # major tick RPM step (adaptive)
        self._tick_count = 0  # number of minor ticks (computed)

        self.min_label = Label(
            text="0",
            font=load_font(size=26, dir="digital", name=self.font_name),
            color=Color.LIGHT_GREY.rgb(),
            pos=(0, 0),
            center=False,
        )
        self.max_label = Label(
            text=str(self._max_rpm),
            font=load_font(size=26, dir="digital", name=self.font_name),
            color=Color.LIGHT_GREY.rgb(),
            pos=(0, 0),
            center=False,
        )

        self._recompute_geometry()

    @property
    def max_rpm(self):
        return self._max_rpm

    @max_rpm.setter
    def max_rpm(self, value):
        self._max_rpm = max(1, int(value))
        self.current_rpm = max(0, min(self.current_rpm, self._max_rpm))
        self.max_label.set_text(str(self._normalize(self._max_rpm)))
        self._recompute_geometry()

    @property
    def width(self):
        return self._width

    @width.setter
    def width(self, value):
        self._width = max(1, int(value))
        self._recompute_geometry()

    @property
    def redline_rpm(self):
        return self._redline_rpm

    @redline_rpm.setter
    def redline_rpm(self, value):
        self._redline_rpm = max(0, int(value))

    @property
    def alert_min(self):
        return self._alert_min

    @alert_min.setter
    def alert_min(self, value):
        self._alert_min = max(0, int(value))

    @property
    def alert_max(self):
        return self._alert_max

    @alert_max.setter
    def alert_max(self, value):
        self._alert_max = max(0, int(value))

    def _normalize(self, value):
        return int(value * 0.001)

    def _rpm_to_x(self, bar_left, rpm):
        t = 0.0 if self._max_rpm == 0 else (rpm / float(self._max_rpm))
        return bar_left + round(t * self._width)

    def _recompute_geometry(self):
        """
        Choose an adaptive minor tick step so that each tick is at least
        _min_px_per_tick wide. Round to the nearest 100 RPM for nice scales.
        """
        # how many minor ticks could we fit given pixel constraint?
        max_minor_ticks_by_pixels = max(1, self._width // self._min_px_per_tick)

        # desired minor step if we evenly split max_rpm into that many ticks
        raw_step = max(1, math.ceil(self._max_rpm / max_minor_ticks_by_pixels))

        # round to a 'car-friendly' step (nearest 100 rpm)
        step_100s = max(1, math.ceil(raw_step / 100))  # at least 100 rpm
        self._tick_step_rpm = step_100s * 100

        # major ticks every N minor ticks
        self._major_step_rpm = self._tick_step_rpm * self._major_factor

        # actual minor tick count (inclusive end tick in drawing)
        self._tick_count = math.ceil(self._max_rpm / self._tick_step_rpm)

    def update(self, packet: Packet, dt: float | None = None) -> None:
        """Reads values from Packet for current frame dt"""
        rpm_alert = getattr(packet, "rpm_alert", None)

        new_redline = (
            int(getattr(rpm_alert, "min", self.redline_rpm))
            if rpm_alert
            else self.redline_rpm
        )
        new_max = (
            int(getattr(rpm_alert, "max", self.max_rpm)) if rpm_alert else self.max_rpm
        )

        # If these change, setters will recompute geometry
        self.redline_rpm = new_redline
        self.max_rpm = new_max

        self.alert_min = self.redline_rpm

        rpm = int(getattr(packet, "engine_rpm", 0) or 0)
        self.current_rpm = max(0, min(rpm, self._max_rpm))

    def draw(self, surface: Any) -> None:
        x, y = (surface.get_width() // 2, 180)
        bar_left = x - self._width // 2

        # for consistent tick rendering (major/minor + color)
        def _draw_tick(tick_rpm: int, y1: int) -> None:
            tick_x = self._rpm_to_x(bar_left, tick_rpm)
            is_end = tick_rpm >= self._max_rpm  # force last tick to be major
            is_major = is_end or ((tick_rpm % self._major_step_rpm) == 0)
            y2 = y1 + (7 if is_major else 3)
            width = 3 if is_major else 1
            tick_color = (
                Color.LIGHT_RED.rgb()
                if tick_rpm >= self._redline_rpm
                else Color.LIGHT_GREY.rgb()
            )
            pygame.draw.line(surface, tick_color, (tick_x, y1), (tick_x, y2), width)

        # continuous fill mode
        if self._max_rpm >= 0:
            rpm = self.current_rpm
            alert_zone = min(rpm, self._alert_min)
            yellow_zone = max(
                0, min(rpm - self._alert_min, self._redline_rpm - self._alert_min)
            )
            red_zone = max(0, rpm - self._redline_rpm)

            # Green segment
            if alert_zone > 0:
                pygame.draw.rect(
                    surface,
                    Color.DARK_GREY.rgb(),  # replace with DARK_GREEN when ready
                    pygame.Rect(
                        bar_left,
                        y,
                        self._rpm_to_x(bar_left, alert_zone) - bar_left,
                        self.height,
                    ),
                )
            # Yellow segment
            if yellow_zone > 0:
                start_x = self._rpm_to_x(bar_left, self._alert_min)
                pygame.draw.rect(
                    surface,
                    Color.DARK_GREY.rgb(),  # replace with DARK_YELLOW when ready
                    pygame.Rect(
                        start_x,
                        y,
                        self._rpm_to_x(bar_left, self._alert_min + yellow_zone)
                        - start_x,
                        self.height,
                    ),
                )
            # Red segment
            if red_zone > 0:
                start_x = self._rpm_to_x(bar_left, self._redline_rpm)
                pygame.draw.rect(
                    surface,
                    Color.RED.rgb(),
                    pygame.Rect(
                        start_x,
                        y,
                        self._rpm_to_x(bar_left, self._redline_rpm + red_zone)
                        - start_x,
                        self.height,
                    ),
                )

            sparse_factor = 2  # skip every other minor tick
            y1 = y + self.height
            minor_count = self._tick_count + 1
            for i in range(0, minor_count, sparse_factor):
                tick_rpm = min(i * self._tick_step_rpm, self._max_rpm)
                _draw_tick(tick_rpm, y1)

            # Ensure the last tick is drawn bold even if skipped by sparse step
            if (minor_count - 1) % sparse_factor != 0:
                _draw_tick(self._max_rpm, y1)

        # labels
        self.max_label.set_text(str(self._normalize(self._max_rpm)))
        pad = 4
        label_y = y + self.height + 2
        self.min_label.rect.topleft = (
            bar_left - self.min_label.surface.get_width() - pad,
            label_y,
        )
        self.max_label.rect.topleft = (bar_left + self._width + pad, label_y)
        self.min_label.draw(surface)
        self.max_label.draw(surface)
