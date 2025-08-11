from os.path import join

import pygame

from ..core.events import (
    BACK_TO_MENU_PRESSED,
    BACK_TO_MENU_RELEASED,
    MAINMENU_SETTINGS_PRESSED,
    MAINMENU_SETTINGS_RELEASED,
    MAINMENU_START_PRESSED,
    MAINMENU_START_RELEASED,
)
from ..widgets.button import Button, ButtonGroup
from ..widgets.label import Label
from ..widgets.properties.colors import Color
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
                    (300, 180, 200, 60),
                    "Start",
                    event_type_pressed=MAINMENU_START_PRESSED,
                    event_type_released=MAINMENU_START_RELEASED,
                ),
                Button(
                    (300, 280, 200, 60),
                    "Settings",
                    event_type_pressed=MAINMENU_SETTINGS_PRESSED,
                    event_type_released=MAINMENU_SETTINGS_RELEASED,
                ),
                Button(
                    (pygame.display.get_surface().get_width() - 80, 20, 60, 60),
                    "x",
                    event_type_pressed=BACK_TO_MENU_PRESSED,
                    event_type_released=BACK_TO_MENU_RELEASED,
                    font=pygame.font.Font(join("assets", "fonts", "pixeltype.ttf"), 48),
                ),
            ]
        )

        self.title_label = Label(
            text="Main Menu",
            font_path=join("assets", "fonts", "pixeltype.ttf"),
            font_size=68,
            color=Color.WHITE.rgb(),
            pos=(320, 100),
            center=False,
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
        from .enter_ip_state import EnterIPState

        self.state_manager.change_state(
            EnterIPState(
                self.state_manager,
            )
        )

    def on_settings_released(self, event):
        RESOLUTIONS = [(1024, 600), (1280, 720)]
        w, h = pygame.display.get_surface().get_size()
        try:
            current_res_index = RESOLUTIONS.index((w, h))
        except ValueError:
            current_res_index = 0  # fallback

        from .settings_state import SettingsState

        self.state_manager.change_state(
            SettingsState(
                self.state_manager,
                RESOLUTIONS,
                current_res_index,
            )
        )

    def update(self, dt):
        super().update(dt)

    def draw(self, surface):
        surface.fill(Color.BLACK.rgb())
        self.title_label.draw(surface)
        self.button_group.draw(surface)
