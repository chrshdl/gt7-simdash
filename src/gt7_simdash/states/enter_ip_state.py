from typing import TYPE_CHECKING, Iterable

import pygame

from gt7_simdash.core.utils import FontFamily, load_font

from ..core.events import (
    BACK_TO_MENU_PRESSED,
    BACK_TO_MENU_RELEASED,
    ENTER_IP_DEL_BUTTON_PRESSED,
    ENTER_IP_DEL_BUTTON_RELEASED,
    ENTER_IP_KEYPAD_BUTTON_PRESSED,
    ENTER_IP_KEYPAD_BUTTON_RELEASED,
    ENTER_IP_OK_BUTTON_PRESSED,
    ENTER_IP_OK_BUTTON_RELEASED,
)
from .state import State

if TYPE_CHECKING:
    pass

from ..widgets.base.button import Button, ButtonGroup
from ..widgets.base.colors import Color
from ..widgets.base.label import Label
from ..widgets.base.textfield import TextField

BUTTONS_PER_ROW = 3
BUTTON_DIMENSIONS = (114, 66)
BUTTON_MARGIN = 7
BUTTON_GRID_OFFSET = (
    BUTTON_DIMENSIONS[0] + BUTTON_MARGIN,
    BUTTON_DIMENSIONS[1] + BUTTON_MARGIN,
)
NUMPAD_OFFSET = (62, 228)


RECENT_BUTTONS_PER_ROW = 1
RECENT_BUTTONS_DIMENSIONS = (260, 70)
RECENT_BUTTONS_MARGIN = 7
RECENT_BUTTONS_GRID_OFFSET = (
    RECENT_BUTTONS_DIMENSIONS[0] + RECENT_BUTTONS_MARGIN,
    RECENT_BUTTONS_DIMENSIONS[1] + RECENT_BUTTONS_MARGIN,
)
RECENT_BUTTONS_OFFSET = (650, 143)


class EnterIPState(State):
    def __init__(self, state_manager=None):
        super().__init__()
        self.state_manager = state_manager
        self.input_text = ""
        self.button_group: ButtonGroup = ButtonGroup()
        labels = list("123456789#0.")

        back_button = Button(
            (pygame.display.get_surface().get_width() - 80, 20, 60, 60),
            "x",
            BACK_TO_MENU_PRESSED,
            BACK_TO_MENU_RELEASED,
            font=load_font(48, FontFamily.PIXEL_TYPE),
        )
        del_button = Button(
            rect=(416, 142, 100, 76),
            text="<",
            event_type_pressed=ENTER_IP_DEL_BUTTON_PRESSED,
            event_type_released=ENTER_IP_DEL_BUTTON_RELEASED,
            font=load_font(50, FontFamily.PIXEL_TYPE),
            color=Color.LIGHT_RED.rgb(),
        )

        ok_button = Button(
            rect=(424, 373, 100, 140),
            text="OK",
            event_type_pressed=ENTER_IP_OK_BUTTON_PRESSED,
            event_type_released=ENTER_IP_OK_BUTTON_RELEASED,
            font=load_font(50, FontFamily.PIXEL_TYPE),
            color=Color.GREEN.rgb(),
        )

        self.button_group.extend(
            self._button_grid_generator(
                labels,
                BUTTONS_PER_ROW,
                BUTTON_GRID_OFFSET,
                NUMPAD_OFFSET,
                BUTTON_DIMENSIONS,
            )
        )
        self.button_group.add(back_button)
        self.button_group.add(del_button)
        self.button_group.add(ok_button)

        self.border_thickness = 2
        self.border_radius = 4

        self.title_label = Label(
            text="Enter PlayStation IP",
            font_name=FontFamily.PIXEL_TYPE,
            font_size=68,
            color=Color.BLUE.rgb(),
            pos=(382, 100),
            center=True,
        )
        self.textfield = TextField(
            text="10.22.33.27",
            font_name=FontFamily.DIGITAL_7_MONO,
            font_size=40,
            color=Color.WHITE.rgb(),
            pos=(62, 142),
            width=356,
            height=76,
            border_color=Color.GREY.rgb(),
        )

    def draw(self, surface):
        surface.fill(Color.BLACK.rgb())
        self.title_label.draw(surface)
        self.textfield.draw(surface)
        self.button_group.draw(surface)

    def handle_event(self, event):
        self.button_group.handle_event(event)
        self.textfield.handle_event(event)

        if event.type == BACK_TO_MENU_RELEASED:
            self.on_back_released(event)
        elif event.type in (
            ENTER_IP_KEYPAD_BUTTON_RELEASED,
            ENTER_IP_DEL_BUTTON_RELEASED,
        ):
            self.on_keypad_released(event)
        elif event.type == ENTER_IP_OK_BUTTON_RELEASED:
            self.on_ok_released(event)

    def on_back_released(self, event):
        from .main_menu_state import MainMenuState

        self.state_manager.change_state(MainMenuState(self.state_manager))

    def on_ok_released(self, event):
        ip = self.textfield.text.strip()
        if self.is_valid_ipv4(ip):
            from .connecting_state import ConnectingState

            next_state = ConnectingState(self.state_manager, ip)
            self.state_manager.change_state(next_state)

    def on_keypad_released(self, event):
        label = getattr(event, "label", None)
        if not label:
            return

        if label == ".":
            if (
                self.textfield.text.count(".") < 3
                and "." not in self.textfield.text[-1:]
            ):
                self.textfield.text += "."
        elif label == "#":
            pass
        elif label == "<":
            self.textfield.text = self.textfield.text[:-1]
        else:
            if len(self.textfield.text) < 15:
                self.textfield.text += label

    def is_valid_ipv4(self, ip_str):
        parts = ip_str.split(".")
        if len(parts) != 4:
            return False
        for part in parts:
            if part == "":
                return False
            if len(part) > 1 and part.startswith("0"):
                return False
            num = int(part)
            if num < 0 or num > 255:
                return False
        return True

    def update(self, dt):
        super().update(dt)
        self.textfield.update(dt)

    def _button_grid_generator(
        self,
        labels: Iterable[str],
        buttons_per_row: int,
        grid_offset: tuple[int, int],
        global_offset: tuple[int, int],
        button_size: tuple[int, int],
    ) -> list[Button]:
        return [
            Button(
                rect=(
                    i % buttons_per_row * grid_offset[0] + global_offset[0],
                    i // buttons_per_row * grid_offset[1] + global_offset[1],
                    button_size[0],
                    button_size[1],
                ),
                text=val,
                event_type_pressed=ENTER_IP_KEYPAD_BUTTON_PRESSED,
                event_type_released=ENTER_IP_KEYPAD_BUTTON_RELEASED,
                event_data={"label": val},
                font=load_font(50, FontFamily.PIXEL_TYPE),
            )
            for i, val in enumerate(labels)
        ]
