import glob
import os
from typing import Optional, Tuple

import pygame

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
from ..widgets.base.label import Label
from .state import State
from .state_manager import StateManager


class _Backlight:
    """
    Minimal helper for Linux backlight sysfs.
    Looks for /sys/class/backlight/*/brightness and max_brightness.
    """

    def __init__(self):
        self._brightness_path: Optional[str] = None
        self._max_path: Optional[str] = None
        self._detect_paths()

    def _detect_paths(self):
        candidates = glob.glob("/sys/class/backlight/*/brightness")
        if candidates:
            self._brightness_path = candidates[0]
            self._max_path = os.path.join(
                os.path.dirname(self._brightness_path), "max_brightness"
            )

    def available(self) -> bool:
        return self._brightness_path is not None and os.path.exists(
            self._brightness_path
        )

    def _read_int(self, path: str) -> Optional[int]:
        try:
            with open(path, "r") as f:
                return int(f.read().strip())
        except Exception:
            return None

    def get_raw(self) -> Optional[Tuple[int, int]]:
        if not self.available():
            return None
        cur = self._read_int(self._brightness_path)
        maxv = self._read_int(self._max_path) if self._max_path else None
        if cur is None or maxv is None or maxv <= 0:
            return None
        return cur, maxv

    def get_percent(self) -> Optional[int]:
        raw = self.get_raw()
        if not raw:
            return None
        cur, maxv = raw
        return int(round((cur / maxv) * 100.0))

    def set_percent(self, percent: float) -> bool:
        """Clamp 0..100, convert to raw, write. Returns True on success."""
        if not self.available():
            return False
        raw = self.get_raw()
        if not raw:
            return False
        _, maxv = raw
        p = max(0, min(100, int(round(percent))))
        value = int(round((p / 100.0) * maxv))
        try:
            with open(self._brightness_path, "w") as f:
                f.write(str(value))
            return True
        except Exception:
            return False


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

        self.brightness_label = Label(
            text="Brightness",
            font=load_font(size=44, dir="pixeltype", name=FontFamily.PIXEL_TYPE),
            color=Color.WHITE.rgb(),
            pos=(320, 220),
            center=True,
        )

        self.back_button = Button(
            rect=(pygame.display.get_surface().get_width() - 80, 20, 60, 60),
            text="x",
            event_type_pressed=BACK_TO_MENU_PRESSED,
            event_type_released=BACK_TO_MENU_RELEASED,
            font=load_font(48, name=FontFamily.PIXEL_TYPE),
            color=Color.WHITE.rgb(),
            antialias=False,
        )

        surf = pygame.display.get_surface()
        center_x = surf.get_width() // 2
        y = 280

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
            color=Color.WHITE.rgb(),
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
            color=Color.WHITE.rgb(),
            antialias=True,
        )

        self.button_group = ButtonGroup()
        self.button_group.add(self.back_button)
        self.button_group.add(self.minus_button)
        self.button_group.add(self.plus_button)

        self._bl = _Backlight()
        self._brightness_percent: Optional[int] = None
        self._error: Optional[str] = None

    def enter(self):
        super().enter()

        if self._bl.available():
            cur = self._bl.get_percent()
            if cur is not None:
                self._brightness_percent = cur
                self._error = None
            else:
                self._brightness_percent = None
                self._error = "Failed to read backlight value."
        else:
            self._brightness_percent = None
            self._error = "No backlight device found."

    def handle_event(self, event):
        self.button_group.handle_event(event)

        if event.type == BACK_TO_MENU_RELEASED:
            self.on_back_released(event)

        elif event.type == BRIGHTNESS_DOWN_RELEASED:
            self._adjust_brightness(-self.STEP_PERCENT)

        elif event.type == BRIGHTNESS_UP_RELEASED:
            self._adjust_brightness(+self.STEP_PERCENT)

    def _adjust_brightness(self, delta_percent: int):
        if self._brightness_percent is None:
            cur = self._bl.get_percent()
            if cur is None:
                self._error = "Backlight not available."
                return
            self._brightness_percent = cur

        target = max(0, min(100, self._brightness_percent + delta_percent))
        if self._bl.set_percent(target):
            self._brightness_percent = target
            self._error = None
        else:
            self._error = "Failed to write brightness."

    def draw(self, surface):
        surface.fill(Color.BLACK.rgb())

        self.title_label.draw(surface)
        self.brightness_label.draw(surface)

        self.button_group.draw(surface)

        value_x = (self.minus_button.rect.right + self.plus_button.rect.left) // 2
        center_y = self.minus_button.rect.centery

        val_font = load_font(size=46, dir="pixeltype", name=FontFamily.PIXEL_TYPE)
        if self._brightness_percent is not None:
            pct_txt = val_font.render(
                f"{self._brightness_percent} %", False, Color.WHITE.rgb()
            )
            pct_rect = pct_txt.get_rect(center=(value_x, center_y))
            surface.blit(pct_txt, pct_rect.topleft)

        if self._error:
            err_font = load_font(size=46, dir="pixeltype", name=FontFamily.PIXEL_TYPE)
            err_txt = err_font.render(self._error, False, Color.DARK_RED.rgb())
            y_under = (
                max(self.minus_button.rect.bottom, self.plus_button.rect.bottom) + 24
            )
            err_rect = err_txt.get_rect(midtop=(value_x, y_under))
            surface.blit(err_txt, err_rect.topleft)

    def on_back_released(self, event):
        from .main_menu_state import MainMenuState

        self.state_manager.change_state(MainMenuState(self.state_manager))

    def update(self, dt):
        super().update(dt)

        if self._bl.available():
            cur = self._bl.get_percent()
            if cur is not None:
                self._brightness_percent = cur
