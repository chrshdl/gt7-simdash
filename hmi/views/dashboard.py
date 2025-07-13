import pygame

from hmi.views.view import View
from hmi.widgets.button import Button
from hmi.widgets.carsor import Carsor
from hmi.widgets.gear import GearIndicator
from hmi.widgets.lap import BestLap, EstimatedLap, Laps
from hmi.widgets.led import LED
from hmi.widgets.minimap import Minimap
from hmi.widgets.rpm import GraphicalRPM, SimpleRPM
from hmi.widgets.speed import Speedometer


class Dashboard(View):
    def __init__(self):
        super().__init__()

        SimpleRPM(self.sprite_group, 76, 33)
        GraphicalRPM(self.sprite_group, 100, 40)
        GearIndicator(self.sprite_group, 200, 248)
        Speedometer(self.sprite_group, 200, 150)
        Laps(self.sprite_group, 127, 96)
        EstimatedLap(self.sprite_group, 260, 104)
        BestLap(self.sprite_group, 260, 104)
        Minimap(self.sprite_group, 350, 350)
        Carsor(self.sprite_group, 350, 350)
        LED()

        # PSL = Pit Speed Limiter
        # ASM = Active Stability Management
        # TCS = Traction Control System
        labels = ["ASM", "TCS", "LIGHTS", "HIBEAM"]
        self.buttons = [
            Button(f"{labels[i]}", ((125 * (i % 4) + 120), 558), (115, 50), 40)
            for i in range(len(labels))
        ]

    def update_rpm_alerts(self, rpmin, rpmax):
        for sprite in self.sprite_group.sprites():
            if isinstance(sprite, SimpleRPM):
                sprite.alert_min(rpmin)
                sprite.alert_max(rpmax)
