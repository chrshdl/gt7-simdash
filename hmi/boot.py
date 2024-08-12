import pygame
from hmi.widgets.connection import Connection
from hmi.properties import Color


class Boot:
    def __init__(self, playstation_ip):
        self.screen = pygame.display.get_surface()
        self.popups = pygame.sprite.Group()

        Connection(self.popups, playstation_ip, 500, 45)

    def update(self, packet, events):
        self.screen.fill(Color.BLACK.rgb())
        self.popups.update(packet)
        self.popups.draw(self.screen)
