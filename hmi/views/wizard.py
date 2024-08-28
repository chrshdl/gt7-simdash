import pygame

from common.ipv4 import get_ip_prefill
from hmi.widgets.button import Button
from hmi.widgets.textfield import Textfield

BUTTONS_PER_ROW = 3
BUTTON_DIMENSIONS = (100, 60)
BUTTON_MARGIN = 20
NUMPAD_OFFSET_X = 70
NUMPAD_OFFSET_Y = 250


class Wizard:
    def __init__(self):
        self.screen = pygame.display.get_surface()
        self.wizard = pygame.sprite.Group()

        self.tf = Textfield(self.wizard, 360, 80, text=get_ip_prefill())

        labels = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "<", "0", "."]
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
        self.buttons.append(Button("OK", (450, 142), (100, 75)))

    def handle_events(self, events):
        for button in self.buttons:
            button.render(self.screen)
            if button.is_pressed(events):
                self.tf.append(button.text)

    def update(self, packet):
        self.wizard.update(packet)
        self.wizard.draw(self.screen)
