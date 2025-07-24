from os.path import join

import pygame

import states
from events import (
    BACK_TO_MENU_PRESSED,
    BACK_TO_MENU_RELEASED,
    DROP_DOWN_PRESSED,
    DROP_DOWN_RELEASED,
    DROP_DOWN_SELECTED,
)
from states.state import State
from states.state_manager import StateManager
from widgets.button import Button, ButtonGroup
from widgets.dropdown import Dropdown
from widgets.properties.colors import Color


class SettingsState(State):
    def __init__(self, state_manager, resolutions, current_res_index):
        super().__init__()
        self.state_manager: StateManager = state_manager
        self.dropdown = Dropdown(
            rect=(300, 180, 240, 60),
            options=resolutions,
            selected_index=current_res_index,
            event_type_pressed=DROP_DOWN_PRESSED,
            event_type_released=DROP_DOWN_RELEASED,
            event_type_select=DROP_DOWN_SELECTED,
        )

        self.back_button = Button(
            (pygame.display.get_surface().get_width() - 80, 20, 60, 60),
            "x",
            BACK_TO_MENU_PRESSED,
            BACK_TO_MENU_RELEASED,
            font=pygame.font.Font(join("assets", "fonts", "pixeltype.ttf"), 48),
        )

        self.button_group = ButtonGroup()
        self.button_group.add(self.back_button)

    def reposition_back_button(self):
        width = pygame.display.get_surface().get_width()
        self.back_button.rect.topleft = (width - 80, 20)

    def enter(self):
        super().enter()

    def handle_event(self, event):
        self.button_group.handle_event(event)
        self.dropdown.handle_event(event)
        if event.type == BACK_TO_MENU_RELEASED:
            self.on_back_released(event)
        elif event.type == DROP_DOWN_SELECTED:
            self.on_resolution_selected(event)

    def draw(self, surface):
        surface.fill(Color.BLACK.rgb())

        font = pygame.font.Font(join("assets", "fonts", "pixeltype.ttf"), 68)
        label = font.render("Settings", False, Color.WHITE.rgb())
        surface.blit(label, (320, 100))
        self.button_group.draw(surface)
        self.dropdown.draw(surface)

    def on_resolution_selected(self, event: pygame.event.Event):
        new_res = event.resolution
        pygame.display.set_mode(new_res)
        self.reposition_back_button()

    def on_back_released(self, event):
        self.state_manager.change_state(states.MainMenuState(self.state_manager))

    def update(self, dt):
        super().update(dt)
