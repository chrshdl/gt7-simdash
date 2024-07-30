import pygame
from hmi.speed import Speedometer
from hmi.gear import GearIndicator
from hmi.rpm import RPM
from hmi.debug import DebugScreen
from hmi.lap import Laps, EstimatedLap, BestLap
from hmi.properties import Color


class HMI:
    def __init__(self):
        self.screen = pygame.display.get_surface()
        self.telemetry = pygame.sprite.Group()

        Speedometer(self.telemetry, 180, 130)
        GearIndicator(self.telemetry, 180, 220)
        RPM(self.telemetry, 300, 33)
        Laps(self.telemetry, 180, 85)
        EstimatedLap(self.telemetry, 185, 85)
        BestLap(self.telemetry, 185, 85)
        DebugScreen(self.telemetry, 180, 110)

    def draw(self, packet):
        self.screen.fill(Color.BLACK.rgb())
        self.telemetry.update(packet)
        self.telemetry.draw(self.screen)

    def update_rpm_alerts(self, rpm_min, rpm_max):
        for sprite in self.telemetry.sprites():
            if isinstance(sprite, RPM):
                sprite.alert_min(rpm_min)
                sprite.alert_max(rpm_max)
