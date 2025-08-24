from typing import Optional

import pygame

from ..core.backlight import Backlight
from ..core.events import (
    BACK_TO_MENU_PRESSED,
    BACK_TO_MENU_RELEASED,
    BRIGHTNESS_DOWN_PRESSED,
    BRIGHTNESS_DOWN_RELEASED,
    BRIGHTNESS_UP_PRESSED,
    BRIGHTNESS_UP_RELEASED,
)
from ..core.utils import FontFamily, load_font
from ..widgets.base.button import Button, ButtonGroup
from ..widgets.base.colors import Color
from ..widgets.base.container import Container
from ..widgets.base.label import Label
from .state import State
from .state_manager import StateManager


class SettingsState(State):
    STEP_PERCENT = 10

    def __init__(self, state_manager):
        super().__init__()
        self.state_manager: StateManager = state_manager

        self.title_label = Label(
            text="Settings",
            font=load_font(size=68, dir="pixeltype", name=FontFamily.PIXEL_TYPE),
            color=Color.WHITE.rgb(),
            pos=(320, 100),
            center=True,
        )

        self.back_button = Button(
            rect=(pygame.display.get_surface().get_width() - 80, 20, 60, 60),
            text="x",
            event_type_pressed=BACK_TO_MENU_PRESSED,
            event_type_released=BACK_TO_MENU_RELEASED,
            font=load_font(48, name=FontFamily.PIXEL_TYPE),
            text_color=Color.WHITE.rgb(),
            antialias=False,
        )
        self.nav_group = ButtonGroup()
        self.nav_group.add(self.back_button)

        surf = pygame.display.get_surface()
        center_x = surf.get_width() // 2
        y = 280

        self.brightness_label = Label(
            text="Brightness",
            font=load_font(size=44, dir="pixeltype", name=FontFamily.PIXEL_TYPE),
            color=Color.WHITE.rgb(),
            pos=(320, 220),
            center=True,
        )

        self.minus_button = Button(
            rect=(center_x - 180, y, 80, 80),
            text="-",
            icon="\ue15b",
            icon_size=46,
            icon_position="center",
            text_visible=False,
            event_type_pressed=BRIGHTNESS_DOWN_PRESSED,
            event_type_released=BRIGHTNESS_DOWN_RELEASED,
            font=load_font(76, name=FontFamily.PIXEL_TYPE),
            text_color=Color.WHITE.rgb(),
            antialias=True,
        )
        self.plus_button = Button(
            rect=(center_x + 60, y, 80, 80),
            text="+",
            icon="\ue145",
            icon_size=46,
            icon_position="center",
            text_visible=False,
            event_type_pressed=BRIGHTNESS_UP_PRESSED,
            event_type_released=BRIGHTNESS_UP_RELEASED,
            font=load_font(76, name=FontFamily.PIXEL_TYPE),
            text_color=Color.WHITE.rgb(),
            antialias=True,
        )

        self.brightness_group = ButtonGroup()
        self.brightness_group.add(self.minus_button)
        self.brightness_group.add(self.plus_button)

        self.brightness_container = Container(is_visible=True)
        self.brightness_container.add(self.brightness_label, self.brightness_group)

        self._backlight = Backlight()
        self._brightness_percent: Optional[int] = None
        self._error: Optional[str] = None

    def enter(self):
        super().enter()

        if self._backlight.available():
            cur = self._backlight.get_percent()
            if cur is not None:
                self._brightness_percent = cur
                self._error = None
            else:
                self._brightness_percent = None
                self._error = "Failed to read backlight value."
        else:
            self._brightness_percent = None
            self._error = "No backlight device found."

        # Container visibility is driven by availability
        self.brightness_container.is_visible = self._backlight.available()

    def handle_event(self, event):
        self.nav_group.handle_event(event)

        self.brightness_container.handle_event(event)

        if event.type == BACK_TO_MENU_RELEASED:
            self.on_back_released(event)

        if self.brightness_container.is_visible and self._backlight.available():
            if event.type == BRIGHTNESS_DOWN_RELEASED:
                self._adjust_brightness(-self.STEP_PERCENT)
            elif event.type == BRIGHTNESS_UP_RELEASED:
                self._adjust_brightness(+self.STEP_PERCENT)

    def _adjust_brightness(self, delta_percent: int):
        if self._brightness_percent is None:
            cur = self._backlight.get_percent()
            if cur is None:
                self._error = "Backlight not available."
                return
            self._brightness_percent = cur

        target = max(0, min(100, self._brightness_percent + delta_percent))
        if self._backlight.set_percent(target):
            self._brightness_percent = target
            self._error = None
        else:
            self._error = "Failed to write brightness."

    def draw(self, surface):
        surface.fill(Color.BLACK.rgb())

        self.title_label.draw(surface)
        self.nav_group.draw(surface)

        self.brightness_container.draw(surface)

        if (
            self.brightness_container.is_visible
            and self._brightness_percent is not None
        ):
            value_x = (self.minus_button.rect.right + self.plus_button.rect.left) // 2
            center_y = self.minus_button.rect.centery
            val_font = load_font(size=46, dir="pixeltype", name=FontFamily.PIXEL_TYPE)
            pct_txt = val_font.render(
                f"{self._brightness_percent} %", False, Color.WHITE.rgb()
            )
            pct_rect = pct_txt.get_rect(center=(value_x, center_y))
            surface.blit(pct_txt, pct_rect.topleft)

        # Error text:
        # - If visible: show it UNDER the buttons
        # - If hidden: still show the message where the controls would be
        if self._error:
            err_font = load_font(size=46, dir="pixeltype", name=FontFamily.PIXEL_TYPE)
            err_txt = err_font.render(self._error, False, Color.DARK_RED.rgb())

            # Place below the buttons (or where they'd be)
            if self.brightness_container.is_visible:
                y_under = (
                    max(self.minus_button.rect.bottom, self.plus_button.rect.bottom)
                    + 24
                )
                value_x = (
                    self.minus_button.rect.right + self.plus_button.rect.left
                ) // 2
                err_rect = err_txt.get_rect(midtop=(value_x, y_under))
            else:
                # Fallback position if controls are hidden
                surf = pygame.display.get_surface()
                value_x = surf.get_width() // 2
                y_under = 300  # roughly where controls would start
                err_rect = err_txt.get_rect(midtop=(value_x, y_under))
            surface.blit(err_txt, err_rect.topleft)

    def on_back_released(self, event):
        from .main_menu_state import MainMenuState

        self.state_manager.change_state(MainMenuState(self.state_manager))

    def update(self, dt):
        super().update(dt)

        # Keep container visibility in sync with hardware state
        avail = self._backlight.available()
        if avail:
            cur = self._backlight.get_percent()
            if cur is not None:
                self._brightness_percent = cur
        self.brightness_container.is_visible = avail
