import pygame

from hmi.widgets.led import LED
from hmi.widgets.rpm import SimpleRPM, GraphicalRPM
from hmi.widgets.gear import GearIndicator
from hmi.widgets.speed import Speedometer
from hmi.widgets.lap import Laps, BestLap, EstimatedLap
from hmi.properties import Color
from hmi.widgets.button import Button
from hmi.widgets.minimap import Minimap
from events import HMI_VIEW_BUTTON_PRESSED


class Dashboard:
    def __init__(self):
        self.screen = pygame.display.get_surface()
        self.telemetry = pygame.sprite.Group()

        SimpleRPM(self.telemetry, 76, 33)
        GraphicalRPM(self.telemetry, 100, 40)
        GearIndicator(self.telemetry, 200, 240)
        Speedometer(self.telemetry, 200, 150)
        Laps(self.telemetry, 120, 104)
        EstimatedLap(self.telemetry, 260, 104)
        BestLap(self.telemetry, 260, 104)
        Minimap(self.telemetry, 300, 300)
        LED()

        # ASM = Active Stability Management
        # TCS = Traction Control System
        labels = ["PSL", "AC", "TCS", "LIGHTS"]
        self.buttons = [
            Button(f"{labels[i]}", ((130 * (i % 4) + 100), 562))
            for i in range(len(labels))
        ]

    def update(self, packet, events):
        self.screen.fill(Color.BLACK.rgb())
        self.telemetry.update(packet)
        self.telemetry.draw(self.screen)

        for button in self.buttons:
            button.update(packet)
            button.render(self.screen)
            if button.is_pressed(events):
                pygame.event.post(
                    pygame.event.Event(HMI_VIEW_BUTTON_PRESSED, message=button.text)
                )

    def update_rpm_alerts(self, rpmin, rpmax):
        for sprite in self.telemetry.sprites():
            if isinstance(sprite, SimpleRPM):
                sprite.alert_min(rpmin)
                sprite.alert_max(rpmax)
