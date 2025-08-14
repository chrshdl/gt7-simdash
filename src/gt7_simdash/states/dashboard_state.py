import pygame
from granturismo.intake.feed import Feed, Packet

from gt7_simdash.widgets.label import Label

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
        self.max_rpm = 9000
        self.redline_rpm = 7500
        self._car_id: int | None = None

        self.rpm_widget = None

        self.logger = Logger(__class__.__name__).get()

        self.back_button = Button(
            rect=(40, 40, 100, 50),
            text="Back",
            event_type_pressed=BACK_TO_MENU_PRESSED,
            event_type_released=BACK_TO_MENU_RELEASED,
        )
        self.speed_label = Label(
            text="0",
            font_name="digital-7-mono",
            font_size=120,
            color=Color.WHITE.rgb(),
            pos=(0, 0),  # will be positioned in draw()
            center=True,
        )
        self.gear_label = Label(
            text="0",
            font_name="digital-7-mono",
            font_size=120,
            color=Color.BLUE.rgb(),
            pos=(0, 0),
            center=True,
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

            speed = int(self.packet.car_speed * 3.6)
            self.speed_label.set_text(f"{speed}")

            gear = int(getattr(self.packet, "current_gear", 0))
            gear_display = "R" if gear == 0 else str(gear)
            self.gear_label.set_text(gear_display)

    def _check_for_car_change(self):
        new_car_id = int(getattr(self.packet, "car_id", -1))
        if new_car_id < 0 or new_car_id == self._car_id:
            return

        self._car_id = new_car_id

        alert_min = int(getattr(self.packet.rpm_alert, "min", 0))
        alert_max = int(getattr(self.packet.rpm_alert, "max", 0))

        self.rpm_widget.redline_rpm = alert_min
        self.rpm_widget.max_rpm = alert_max

    def draw(self, surface):
        surface.fill(Color.BLACK.rgb())

        w, h = surface.get_size()

        self.rpm_widget.draw(surface)

        self.speed_label.rect.center = (w // 2, h // 8)
        self.speed_label.draw(surface)

        self.gear_label.rect.center = (w // 2, h // 2 + 30)
        self.gear_label.draw(surface)
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
