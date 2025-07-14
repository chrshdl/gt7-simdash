import pygame
from granturismo.model import Packet

from hmi.properties import Color


class View:
    def __init__(self):
        self.buttons = []
        self.screen = pygame.display.get_surface()
        self.sprite_group: pygame.sprite.Group = pygame.sprite.Group()

    def handle_view_events(self):
        for button in self.buttons:
            button.update()

    def handle_packet(self, packet: Packet):
        self.screen.fill(Color.BLACK.rgb())
        self.sprite_group.update(packet)
        self.sprite_group.draw(self.screen)

        for button in self.buttons:
            button.handle_packet(packet)
            button.render(self.screen)
