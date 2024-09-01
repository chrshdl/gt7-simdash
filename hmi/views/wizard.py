import pygame

from common.ipv4 import get_ip_prefill
from hmi.properties import Color
from hmi.widgets.button import Button
from hmi.widgets.textfield import Textfield

BUTTONS_PER_ROW = 3
BUTTON_DIMENSIONS = (114, 66)
BUTTON_MARGIN = 7
NUMPAD_OFFSET_X = 62
NUMPAD_OFFSET_Y = 228


class Wizard:
    def __init__(self):
        self.screen = pygame.display.get_surface()
        self.wizard = pygame.sprite.Group()

        self.tf = Textfield(self.wizard, 360, 80, text=get_ip_prefill())

        labels = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "", "0", "."]
        self.buttons = [
            Button(
                f"{val}",
                (
                    i % BUTTONS_PER_ROW * (BUTTON_DIMENSIONS[0] + BUTTON_MARGIN)
                    + NUMPAD_OFFSET_X,
                    i // BUTTONS_PER_ROW * (BUTTON_DIMENSIONS[1] + BUTTON_MARGIN)
                    + NUMPAD_OFFSET_Y,
                ),
                BUTTON_DIMENSIONS,
            )
            for i, val in enumerate(labels)
        ]
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
