import pygame
from granturismo.model import Packet

from hmi.properties import Color
from hmi.widgets.connection import Connection


class Startup:
    def __init__(self, playstation_ip: str):
        self.screen: pygame.Surface = pygame.display.get_surface()
        self.startup: pygame.sprite.Group = pygame.sprite.Group()

        Connection(self.startup, playstation_ip, 600, 46)

    def handle_events(self, _) -> None:
        pass

    def update(self, packet: Packet) -> None:
        self.screen.fill(Color.BLACK.rgb())
        self.startup.update(packet)
        self.startup.draw(self.screen)
