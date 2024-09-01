from collections.abc import Iterable

import pygame

from common.ipv4 import get_ip_prefill
from hmi.properties import Color
from hmi.widgets.button import Button
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
            val,
            (
                i % buttons_per_row * grid_offset[0] + global_offset[0],
                i // buttons_per_row * grid_offset[1] + global_offset[1],
            ),
            button_size,
        )
        for i, val in enumerate(labels)
    ]


RECENT_BUTTONS_DIMENSIONS = (260, 70)
RECENT_BUTTONS_MARGIN = 7
RECENT_BUTTONS_GRID_OFFSET = (
    RECENT_BUTTONS_DIMENSIONS[0] + RECENT_BUTTONS_MARGIN,
    RECENT_BUTTONS_DIMENSIONS[1] + RECENT_BUTTONS_MARGIN,
)
RECENT_BUTTONS_OFFSET = (20, 20)


class Wizard:
    def __init__(self, recent_connected: list[str]):
        self.screen = pygame.display.get_surface()
        self.wizard = pygame.sprite.Group()

        self.tf = Textfield(self.wizard, 360, 80, text=get_ip_prefill())

        labels = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "", "0", "."]
        self.buttons = button_grid_generator(
            labels,
            BUTTONS_PER_ROW,
            BUTTON_GRID_OFFSET,
            NUMPAD_OFFSET,
            BUTTON_DIMENSIONS,
        )
        self.buttons.append(
            Button(
                "OK",
                (430, 373),
                (100, 140),
                text_color=Color.GREEN,
                outline_color=Color.DARK_GREEN,
            )
        )
        self.buttons.append(
            Button(
                "<",
                (430, 142),
                (100, 76),
                text_color=Color.YELLOW,
                outline_color=Color.DARK_YELLOW,
            )
        )
        self.buttons.extend(
            button_grid_generator(
                recent_connected[0:3],
                4,
                RECENT_BUTTONS_GRID_OFFSET,
                RECENT_BUTTONS_OFFSET,
                RECENT_BUTTONS_DIMENSIONS,
            )
        )

    def handle_events(self, events):
        for button in self.buttons:
            button.render(self.screen)
            if button.is_pressed(events):
                pass
            elif button.is_released(events):
                self.tf.append(button.text)

    def update(self, packet):
        self.wizard.update(packet)
        self.wizard.draw(self.screen)
        for button in self.buttons:
            button.update(packet)
            button.render(self.screen)
