import pygame

from hmi.widgets.led import LED
from hmi.widgets.rpm import RPM
from hmi.widgets.gear import GearIndicator
from hmi.widgets.speed import Speedometer
from hmi.widgets.lap import Laps, BestLap, EstimatedLap
from hmi.properties import Color


class View:
    def __init__(self):
        self.screen = pygame.display.get_surface()
        self.telemetry = pygame.sprite.Group()

        RPM(self.telemetry, 300, 33)
        GearIndicator(self.telemetry, 180, 220)
        Speedometer(self.telemetry, 180, 130)
        Laps(self.telemetry, 180, 85)
        EstimatedLap(self.telemetry, 185, 85)
        BestLap(self.telemetry, 185, 85)
        LED()

    def update(self, packet):
        self.screen.fill(Color.BLACK.rgb())
        self.telemetry.update(packet)
        self.telemetry.draw(self.screen)

    def update_rpm_alerts(self, rpmin, rpmax):
        for sprite in self.telemetry.sprites():
            if isinstance(sprite, RPM):
                sprite.alert_min(rpmin)
                sprite.alert_max(rpmax)

