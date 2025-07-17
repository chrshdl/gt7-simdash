from collections.abc import Iterable

import pygame

from common.eventdispatcher import EventDispatcher
from common.ipv4 import get_ip_prefill
from events import (
    HMI_WIZARD_DEL_BUTTON_PRESSED,
    HMI_WIZARD_DEL_BUTTON_RELEASED,
    HMI_WIZARD_KEYPAD_BUTTON_PRESSED,
    HMI_WIZARD_KEYPAD_BUTTON_RELEASED,
    HMI_WIZARD_OK_BUTTON_PRESSED,
    HMI_WIZARD_OK_BUTTON_RELEASED,
)
from hmi.properties import Color
from hmi.views.view import View
from hmi.widgets.button import Button, ButtonState
from hmi.widgets.textfield import Textfield

BUTTONS_PER_ROW = 3
BUTTON_DIMENSIONS = (114, 66)
BUTTON_MARGIN = 7
BUTTON_GRID_OFFSET = (
    BUTTON_DIMENSIONS[0] + BUTTON_MARGIN,
    BUTTON_DIMENSIONS[1] + BUTTON_MARGIN,
)
NUMPAD_OFFSET = (62, 228)


def button_grid_generator(
    labels: Iterable[str],
    buttons_per_row: int,
    grid_offset: tuple[int, int],
    global_offset: tuple[int, int],
    button_size: tuple[int, int],
) -> list[Button]:
    return [
        Button(
            text=val,
            position=(
                i % buttons_per_row * grid_offset[0] + global_offset[0],
                i // buttons_per_row * grid_offset[1] + global_offset[1],
            ),
            size=button_size,
            out_events={
                ButtonState.PRESSED: HMI_WIZARD_KEYPAD_BUTTON_PRESSED,
                ButtonState.RELEASED: HMI_WIZARD_KEYPAD_BUTTON_RELEASED,
            },
        )
        for i, val in enumerate(labels)
    ]


RECENT_BUTTONS_PER_ROW = 1
RECENT_BUTTONS_DIMENSIONS = (260, 70)
RECENT_BUTTONS_MARGIN = 7
RECENT_BUTTONS_GRID_OFFSET = (
    RECENT_BUTTONS_DIMENSIONS[0] + RECENT_BUTTONS_MARGIN,
    RECENT_BUTTONS_DIMENSIONS[1] + RECENT_BUTTONS_MARGIN,
)
RECENT_BUTTONS_OFFSET = (650, 143)


class Wizard(View):
    def __init__(self, recent_connected: list[str]):
        super().__init__()

        for event in (
            HMI_WIZARD_DEL_BUTTON_RELEASED,
            HMI_WIZARD_OK_BUTTON_RELEASED,
            HMI_WIZARD_KEYPAD_BUTTON_RELEASED,
        ):
            EventDispatcher.add_listener(event, self.on_button_released)

        self.tf = Textfield(self.sprite_group, 360, 80, text=get_ip_prefill())

        labels = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "", "0", "."]

        self.button_group.extend(
            button_grid_generator(
                labels,
                BUTTONS_PER_ROW,
                BUTTON_GRID_OFFSET,
                NUMPAD_OFFSET,
                BUTTON_DIMENSIONS,
            )
        )
        self.button_group.add(
            Button(
                "OK",
                (430, 373),
                (100, 140),
                colors={
                    ButtonState.IDLE: (
                        pygame.Color(Color.BLACK.rgb()),
                        pygame.Color(Color.BLACK.rgb()),
                        pygame.Color(Color.GREY.rgb()),
                        pygame.Color(Color.GREEN.rgb()),
                    ),
                    ButtonState.PRESSED: (
                        pygame.Color(Color.DARK_GREEN.rgb()),
                        pygame.Color(Color.BLACK.rgb()),
                        pygame.Color(Color.GREEN.rgb()),
                        pygame.Color(Color.GREEN.rgb()),
                    ),
                    ButtonState.RELEASED: (
                        pygame.Color(Color.BLACK.rgb()),
                        pygame.Color(Color.BLACK.rgb()),
                        pygame.Color(Color.GREY.rgb()),
                        pygame.Color(Color.GREEN.rgb()),
                    ),
                },
                out_events={
                    ButtonState.PRESSED: HMI_WIZARD_OK_BUTTON_PRESSED,
                    ButtonState.RELEASED: HMI_WIZARD_OK_BUTTON_RELEASED,
                },
            )
        )
        self.button_group.add(
            Button(
                "<",
                (430, 142),
                (100, 76),
                colors={
                    ButtonState.IDLE: (
                        pygame.Color(Color.BLACK.rgb()),
                        pygame.Color(Color.BLACK.rgb()),
                        pygame.Color(Color.GREY.rgb()),
                        pygame.Color(Color.LIGHT_RED.rgb()),
                    ),
                    ButtonState.PRESSED: (
                        pygame.Color(Color.DARK_RED.rgb()),
                        pygame.Color(Color.BLACK.rgb()),
                        pygame.Color(Color.LIGHT_RED.rgb()),
                        pygame.Color(Color.LIGHT_RED.rgb()),
                    ),
                    ButtonState.RELEASED: (
                        pygame.Color(Color.BLACK.rgb()),
                        pygame.Color(Color.BLACK.rgb()),
                        pygame.Color(Color.GREY.rgb()),
                        pygame.Color(Color.LIGHT_RED.rgb()),
                    ),
                },
                out_events={
                    ButtonState.PRESSED: HMI_WIZARD_DEL_BUTTON_PRESSED,
                    ButtonState.RELEASED: HMI_WIZARD_DEL_BUTTON_RELEASED,
                },
            )
        )
        self.button_group.extend(
            button_grid_generator(
                recent_connected[0:3],
                RECENT_BUTTONS_PER_ROW,
                RECENT_BUTTONS_GRID_OFFSET,
                RECENT_BUTTONS_OFFSET,
                RECENT_BUTTONS_DIMENSIONS,
            )
        )

    def on_button_released(self, event):
        self.tf.append(event.data)
