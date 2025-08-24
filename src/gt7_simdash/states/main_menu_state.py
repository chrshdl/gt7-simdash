import pygame

from ..core.events import (
    BACK_TO_MENU_PRESSED,
    BACK_TO_MENU_RELEASED,
    MAINMENU_SETTINGS_PRESSED,
    MAINMENU_SETTINGS_RELEASED,
    MAINMENU_START_PRESSED,
    MAINMENU_START_RELEASED,
)
from ..core.utils import FontFamily, load_font
from ..widgets.base.button import Button, ButtonGroup
from ..widgets.base.colors import Color
from .state import State
from .state_manager import StateManager


class MainMenuState(State):
    def __init__(self, state_manager=None):
        super().__init__()
        self.state_manager: StateManager = state_manager
        self.button_group: ButtonGroup = ButtonGroup()
        self.button_group.extend(
            [
                Button(
                    rect=(200, 200, 260, 180),
                    text="Instrument Viz",
                    text_gap=10,
                    event_type_pressed=MAINMENU_START_PRESSED,
                    event_type_released=MAINMENU_START_RELEASED,
                    font=load_font(42, dir="pixeltype", name=FontFamily.PIXEL_TYPE),
                    antialias=False,
                    icon="\ue32f",
                    icon_size=66,
                    icon_position="center",
                    icon_gap=40,
                    content_align="center",
                    padding=(0, 0),
                    icon_cell_width=36,
                ),
                Button(
                    rect=(480, 200, 260, 180),
                    text="Setup",
                    text_color=Color.WHITE.rgb(),
                    text_gap=10,
                    event_type_pressed=MAINMENU_SETTINGS_PRESSED,
                    event_type_released=MAINMENU_SETTINGS_RELEASED,
                    font=load_font(42, dir="pixeltype", name=FontFamily.PIXEL_TYPE),
                    antialias=True,
                    icon="\ue8b8",
                    icon_color=Color.WHITE.rgb(),
                    icon_size=62,
                    icon_position="center",
                    icon_gap=0,
                    content_align="center",
                    padding=(18, 0),
                    icon_cell_width=36,
                ),
                Button(
                    (pygame.display.get_surface().get_width() - 80, 20, 60, 60),
                    "x",
                    event_type_pressed=BACK_TO_MENU_PRESSED,
                    event_type_released=BACK_TO_MENU_RELEASED,
                    font=load_font(48, name=FontFamily.PIXEL_TYPE),
                ),
            ]
        )

    def handle_event(self, event):
        self.button_group.handle_event(event)

        if event.type == MAINMENU_SETTINGS_RELEASED:
            self.on_settings_released(event)
        elif event.type == MAINMENU_START_RELEASED:
            self.on_start_released(event)
        elif event.type == BACK_TO_MENU_RELEASED:
            self.state_manager.running = False

    def on_start_released(self, event):
        from ..config import ConfigManager
        from .enter_ip_state import EnterIPState

        conf = ConfigManager.get_config()
        self.state_manager.change_state(
            EnterIPState(self.state_manager, conf.recent_connected)
        )

    def on_settings_released(self, event):
        from .settings_state import SettingsState

        self.state_manager.change_state(SettingsState(self.state_manager))

    def update(self, dt):
        super().update(dt)

    def draw(self, surface):
        surface.fill(Color.BLACK.rgb())
        self.button_group.draw(surface)
