from os.path import join

import pygame

import states
from events import (
    MAINMENU_SETTINGS_PRESSED,
    MAINMENU_SETTINGS_RELEASED,
    MAINMENU_START_PRESSED,
    MAINMENU_START_RELEASED,
)
from states.state import State
from states.state_manager import StateManager
from widgets.button import Button, ButtonGroup
from widgets.properties.colors import Color


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
            ]
        )

    def handle_event(self, event):
        self.button_group.handle_event(event)

        if event.type == MAINMENU_SETTINGS_RELEASED:
            self.on_settings_released(event)
        elif event.type == MAINMENU_START_RELEASED:
            self.on_start_released(event)

    def on_start_released(self, event):
        self.state_manager.change_state(
            states.EnterIPState(
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

        self.state_manager.change_state(
            states.SettingsState(
                self.state_manager,
                RESOLUTIONS,
                current_res_index,
            )
        )

    def update(self, dt):
        super().update(dt)

    def draw(self, surface):
        surface.fill(Color.BLACK.rgb())
        font = pygame.font.Font(join("assets", "fonts", "pixeltype.ttf"), 68)
        title = font.render("Main Menu", False, Color.WHITE.rgb())
        surface.blit(title, (320, 100))
        self.button_group.draw(surface)
