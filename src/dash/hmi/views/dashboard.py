import io

import pygame
from events import HMI_VIEW_BUTTON_PRESSED, HMI_VIEW_BUTTON_RELEASED
from granturismo.model import Packet
from hmi.properties import Color
from hmi.widgets.button import Button
from hmi.widgets.carsor import Carsor
from hmi.widgets.gear import GearIndicator
from hmi.widgets.lap import BestLap, EstimatedLap, Laps
from hmi.widgets.led import LED
from hmi.widgets.minimap import Minimap
from hmi.widgets.rpm import GraphicalRPM, SimpleRPM  # noqa: F401
from hmi.widgets.speed import Speedometer


class Dashboard:
    def __init__(self):
        self.screen = pygame.display.get_surface()
        self.telemetry = pygame.sprite.Group()

        # SimpleRPM(self.telemetry, 76, 33)
        # GraphicalRPM(self.telemetry, 100, 40)
        GearIndicator(self.telemetry, 200, 248)
        Speedometer(self.telemetry, 200, 150)
        Laps(self.telemetry, 127, 96)
        EstimatedLap(self.telemetry, 260, 104)
        BestLap(self.telemetry, 260, 104)
        Minimap(self.telemetry, 300, 300)
        Carsor(self.telemetry, 300, 300)
        LED()

        # PSL = Pit Speed Limiter
        # ASM = Active Stability Management
        # TCS = Traction Control System
        # LIGHTS
        # HIBEAM
        labels = ["Setup"]
        width = 142
        height = 94

        self.buttons = [
            Button(f"{labels[i]}", (((width + 10) * (i % 4) + 10), 600-height+2), (width, height), 40)
            for i in range(len(labels))
        ]

    def handle_events(self, events: list[pygame.event.Event]) -> None:
        for button in self.buttons:
            if button.is_pressed(events):
                pygame.event.post(
                    pygame.event.Event(HMI_VIEW_BUTTON_PRESSED, message=button.text)
                )
            if button.is_released(events):
                pygame.event.post(
                    pygame.event.Event(HMI_VIEW_BUTTON_RELEASED, message=button.text)
                )

    def update(self, packet: Packet):
        self.screen.fill(Color.BLACK.rgb())
        self.telemetry.update(packet)
        self.telemetry.draw(self.screen)

        for button in self.buttons:
            button.update(packet)
            button.render(self.screen)

        # oil_img = self.load_and_scale_svg("assets/Kontrollleuchte_Oeldruck.svg", 0.8)
        # self.screen.blit(oil_img, (420, 542))

        # turn_signal_img = self.load_and_scale_svg("assets/Kontrollleuchte_Oeldruck_black.svg", 0.8)
        # self.screen.blit(turn_signal_img, (520, 542))

        lights_img = self.load_and_scale_svg("assets/A02_Low_Beam_Indicator.svg", 0.25)
        self.screen.blit(lights_img, (630, 544))

        abs_img = self.load_and_scale_svg("assets/Kontrollleuchte_Fernlicht_black.svg", 0.5)
        self.screen.blit(abs_img, (712, 538))

        tc_img = self.load_and_scale_svg("assets/TC.svg", 0.5)
        self.screen.blit(tc_img, (790, 542))

    def update_rpm_alerts(self, rpmin, rpmax):
        for sprite in self.telemetry.sprites():
            if isinstance(sprite, SimpleRPM):
                sprite.alert_min(rpmin)
                sprite.alert_max(rpmax)

    def load_and_scale_svg(self, filename, scale):
        svg_string = open(filename, "rt").read()
        start = svg_string.find('<svg')    
        if start > 0:
            svg_string = svg_string[:start+4] + f' transform="scale({scale})"' + svg_string[start+4:]
        return pygame.image.load(io.BytesIO(svg_string.encode()))