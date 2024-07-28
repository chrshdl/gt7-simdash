import pygame
from hmi.speed import Speedometer
from hmi.gear import GearIndicator
from hmi.rpm import RPM
from hmi.debug import DebugScreen
from hmi.lap import Laps, CurrentLap, BestLap
from hmi.color import Color


class HMI:
    def __init__(self):
        self.screen = pygame.display.get_surface()
        self.telemetry = pygame.sprite.Group()

        Speedometer(self.telemetry, 180, 130)
        GearIndicator(self.telemetry, 180, 220)
        RPM(self.telemetry, 400, 30)
        Laps(self.telemetry, 180, 88)
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
            if isinstance(sprite, RPM):
                sprite.alert_min(rpm_min)
                sprite.alert_max(rpm_max)
