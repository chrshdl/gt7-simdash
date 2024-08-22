import pygame

from hmi.properties import Color
from hmi.widgets.connection import Connection


class Startup:
    def __init__(self, playstation_ip):
        self.screen = pygame.display.get_surface()
        self.startup = pygame.sprite.Group()

        Connection(self.startup, playstation_ip, 600, 46)

    def handle_events(self, events):
        pass

    def update(self, packet):
        self.screen.fill(Color.BLACK.rgb())
        self.startup.update(packet)
        self.startup.draw(self.screen)
