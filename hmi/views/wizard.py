import pygame

from hmi.widgets.button import Button
from hmi.widgets.textfield import Textfield

BUTTONS_PER_ROW = 3
NUMPAD_OFFSET_X = 350
NUMPAD_OFFSET_Y = 280


class Wizard:
    def __init__(self):
        self.screen = pygame.display.get_surface()
        self.wizard = pygame.sprite.Group()

        self.tf = Textfield(self.wizard, 360, 80)

        labels = ["0", ".", "<", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
        self.buttons = [
            Button(
                f"{val}",
                (
                    i % BUTTONS_PER_ROW * 68 + NUMPAD_OFFSET_X,
                    i // BUTTONS_PER_ROW * 60 + NUMPAD_OFFSET_Y,
                ),
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
