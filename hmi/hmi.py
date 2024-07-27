import pygame
from hmi.event import Event
from hmi.speed import Speedometer
from hmi.gear import GearIndicator
from hmi.rpm import RPM
from hmi.debug import DebugScreen
from hmi.lap import Lap, CurrentLap, BestLap
from hmi.color import Color
import logging


class HMI:
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.screen = pygame.display.get_surface()
        self.telemetry = pygame.sprite.Group()

        Speedometer(self.telemetry, 180, 130)
        GearIndicator(self.telemetry, 180, 220)
        RPM(self.telemetry, 400, 30)
        Lap(self.telemetry, 180, 88)
        CurrentLap(self.telemetry, 180, 88)
        BestLap(self.telemetry, 180, 88)
        DebugScreen(self.telemetry, 180, 110)

    def draw(self, dt, packet=None):
        self.screen.fill(Color.BLACK.rgb())
        self.telemetry.update(dt, packet)
        self.telemetry.draw(self.screen)

    def update_rpm_alerts(self, rpm_min, rpm_max):
        sprites = self.telemetry.sprites()
        for sprite in sprites:
            if isinstance(s, RPM):
                sprite.alert_min(rpm_min)
                sprite.alert_max(rpm_max)
