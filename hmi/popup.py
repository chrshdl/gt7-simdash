import pygame
from hmi.widgets.splash import Splash
from hmi.properties import Color


class Popup:
    def __init__(self, playstation_ip):
        self.screen = pygame.display.get_surface()
        self.popups = pygame.sprite.Group()

        Splash(self.popups, playstation_ip, 500, 45)

    def update(self, packet, events):
        self.screen.fill(Color.BLACK.rgb())
        self.popups.update(packet)
        self.popups.draw(self.screen)
