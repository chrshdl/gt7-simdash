import pygame
from hmi.widgets.connection import Connection
from hmi.properties import Color


class Startup:
    def __init__(self, playstation_ip):
        self.screen = pygame.display.get_surface()
        self.startup = pygame.sprite.Group()

        Connection(self.startup, playstation_ip, 600, 46)

    def update(self, packet, events):
        self.screen.fill(Color.BLACK.rgb())
        self.startup.update(packet)
        self.startup.draw(self.screen)
