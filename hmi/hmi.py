import pygame
from hmi.speed import Speedometer
from hmi.gear import GearIndicator
from hmi.debug import DebugScreen
from hmi.color import Color
import logging


class HMI:
    def __init__(self):

        self.logger = logging.getLogger(self.__class__.__name__)
        self.screen = pygame.display.get_surface()
        self.telemetry = pygame.sprite.Group()

        Speedometer(self.telemetry, 180, 130)
        GearIndicator(self.telemetry, 180, 220)
        # self.sprites.add(Lap(180, 88, 10, 10, 48))
        # self.sprites.add(LastLap(180, 88, 610, 10))
        # self.sprites.add(BestLap(180, 88, 610, 372))
        DebugScreen(self.telemetry, 180, 110)

    def draw(self, dt, packet=None):
        self.screen.fill(Color.BLACK.rgb())
        self.telemetry.update(dt, packet)
        self.telemetry.draw(self.screen)
