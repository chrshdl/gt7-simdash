import pygame

from common.ipv4 import get_ip_prefill
from hmi.widgets.button import Button
from hmi.widgets.textfield import Textfield


class Wizard:
    def __init__(self):
        self.screen = pygame.display.get_surface()
        self.wizard = pygame.sprite.Group()

        self.tf = Textfield(self.wizard, 360, 80, text=get_ip_prefill())

        labels = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0", ".", "<", "OK"]
        self.buttons = [
            Button(f"{labels[i]}", (68 * i + 60, 280)) for i in range(len(labels))
        ]

    def handle_events(self, events):
        for button in self.buttons:
            button.render(self.screen)
            if button.is_pressed(events):
                self.tf.append(button.text)

    def update(self, packet):
        self.wizard.update(packet)
        self.wizard.draw(self.screen)
