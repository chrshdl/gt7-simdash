from os.path import join

import pygame
from granturismo.intake.feed import Feed, Packet

from ..core.events import (
    BACK_TO_MENU_PRESSED,
    BACK_TO_MENU_RELEASED,
)
from ..core.logger import Logger
from ..widgets.button import Button, ButtonGroup
from ..widgets.graphical_rpm import GraphicalRPM
from ..widgets.properties.colors import Color
from .state import State


class DashboardState(State):
    def __init__(self, state_manager, feed):
        super().__init__()
        self.state_manager = state_manager
        self.feed: Feed = feed
        self.packet = None
        self.current_rpm = 0
        self.speed = 0
        self.gear = 0
        self.max_rpm = 9000
        self.redline_rpm = 7500
        self._car_id: int | None = None

        self.rpm_widget = None

        self.logger = Logger(__class__.__name__).get()

        self.font_main = pygame.font.Font(
            join("assets", "fonts", "digital-7-mono.ttf"), 120
        )

        self.back_button = Button(
            rect=(40, 40, 100, 50),
            text="Back",
            event_type_pressed=BACK_TO_MENU_PRESSED,
            event_type_released=BACK_TO_MENU_RELEASED,
        )
        self.button_group = ButtonGroup()
        self.button_group.extend([self.back_button])

    def enter(self):
        super().enter()
        w, _ = pygame.display.get_surface().get_size()
        self.rpm_widget = GraphicalRPM(
            pos=(w // 2, 180),
            alert_min=5500,
            alert_max=self.redline_rpm,
            max_rpm=self.max_rpm,
            redline_rpm=self.redline_rpm,
        )

    def handle_event(self, event):
        self.button_group.handle_event(event)
        if event.type == BACK_TO_MENU_RELEASED:
            self.on_back(event)

    def update(self, dt):
        super().update(dt)
        if self.feed is None:
            return
        try:
            packet: Packet = self.feed.get_nowait()
            if packet:
                self.packet = packet
        except Exception as e:
            self.logger.info({e})

        if self.packet:
            self._check_for_car_change()

            current_rpm = int(getattr(self.packet, "engine_rpm", 0))
            self.rpm_widget.update(current_rpm)
            self.speed = int(self.packet.car_speed * 3.6)
            self.gear = int(getattr(self.packet, "current_gear", 0))

    def _check_for_car_change(self):
        """Check telemetry for a new car_id and trigger change handling."""
        new_car_id = int(getattr(self.packet, "car_id", -1))
        if new_car_id < 0 or new_car_id == self._car_id:
            return

        self._car_id = new_car_id

        alert_min = int(getattr(self.packet.rpm_alert, "min", 0))
        alert_max = int(getattr(self.packet.rpm_alert, "max", 0))

        self.rpm_widget.redline_rpm = alert_min
        self.rpm_widget.max_rpm = alert_max

    def draw(self, surface):
        surface.fill((10, 10, 20))

        w, h = surface.get_size()

        self.rpm_widget.draw(surface)

        speed_text = self.font_main.render(f"{self.speed}", False, Color.WHITE.rgb())
        speed_rect = speed_text.get_rect(center=(w // 2, h // 8))
        surface.blit(speed_text, speed_rect)

        gear_display = "R" if self.gear == 0 else str(self.gear)
        gear_text = self.font_main.render(gear_display, False, Color.BLUE.rgb())
        gear_rect = gear_text.get_rect(center=(w // 2, h // 2 + 30))
        surface.blit(gear_text, gear_rect)

        self.button_group.draw(surface)

    def on_back(self, event):
        from .enter_ip_state import EnterIPState

        self.state_manager.change_state(EnterIPState(self.state_manager))

    def exit(self):
        if self.feed is not None:
            try:
                self.feed.close()
            except Exception:  # noqa: S110
                pass  # Error closing feed
            self.feed = None
        super().exit()
