import pygame
from hmi.speed import Speedometer
from hmi.debug import DebugScreen
from hmi.popup import InitializingScreen
from hmi.gear import GearIndicator
from hmi.lap import Lap, LastLap, BestLap
from hmi.rpm import RPM
from hmi.event import Event
from hmi.color import Color
import logging


class HMI:
    def __init__(self, ps5_ip, debug_mode=False, rpm_min=1500, rpm_max=2000, car_id=-1):
        self._started = False
        self._car_id = car_id
        self._ps5_ip = ps5_ip
        self._debug_mode = debug_mode

        self.logger = logging.getLogger(self.__class__.__name__)

        self.screen = pygame.display.get_surface()

        self.initializing = InitializingScreen(
            self.screen.get_size()[0], self.screen.get_size()[1], 0, 0, 40, 56
        )

        self.sprites = pygame.sprite.Group()
        self.sprites.add(Speedometer(180, 130, 310, 10, 108))
        self.sprites.add(GearIndicator(180, 220, 310, 240, 240))
        self.sprites.add(Lap(180, 88, 10, 10, 48))
        self.sprites.add(LastLap(180, 88, 610, 10))
        self.sprites.add(BestLap(180, 88, 610, 372))
        if self._debug_mode:
            self.sprites.add(DebugScreen(180, 110, 610, 250, 40, 32))

        self.rpm = pygame.sprite.Group()
        self.add_rpm(rpm_min, rpm_max)

    def add_rpm(self, rpm_min, rpm_max):
        y = 165

        rpm_min = self._normalize(rpm_min) - 3
        rpm_max = self._normalize(rpm_max) + 10

        screen_width = self.screen.get_size()[0]
        self.rpm.add(
            RPM(screen_width, y, rpm_min, rpm_max, step) for step in range(rpm_max + 1)
        )

    def _normalize(self, value):
        return int(value * 0.01)

    def set_rpm_alerts(self, rpm_min, rpm_max):
        self.remove_all_rpm()
        self.add_rpm(rpm_min, rpm_max)

    def remove_all_rpm(self):
        for item in self.rpm:
            self.rpm.remove(item)

    def update_rpm(self, engine_rpm):
        self.rpm.update(engine_rpm)
        self.rpm.draw(self.screen)

    def update_sprites(self, packet):
        self.sprites.update(packet)
        self.sprites.draw(self.screen)

    @property
    def debug_mode(self):
        return self._debug_mode

    @debug_mode.setter
    def debug_mode(self, value):
        self._debug_mode = value

    @property
    def ps5_ip(self):
        return self._ps5_ip

    @ps5_ip.setter
    def ps5_ip(self, value):
        self.ps5_ip = value

    @property
    def car_id(self):
        return self._car_id

    @car_id.setter
    def car_id(self, new_car_id):
        if self._car_id != new_car_id:
            self._car_id = new_car_id
            self._on_car_id_change()

    @property
    def started(self):
        return self._started

    def start(self):
        if not self._started:
            self._started = True
            self._on_started()

    def _on_car_id_change(self):
        self.logger.info(f"emitting {Event.NEW_CAR_EVENT.name()}")
        pygame.event.post(
            pygame.event.Event(Event.NEW_CAR_EVENT.type(), message=self._car_id)
        )

    def _on_started(self):
        self.logger.info(f"emitting {Event.HMI_STARTED_EVENT.name()}")
        pygame.event.post(
            pygame.event.Event(Event.HMI_STARTED_EVENT.type(), message=self._started)
        )

    def draw_text(self, text):
        self.initializing.update(text)
        self.screen.blit(self.initializing.image, (0, 0))
        pygame.display.update()

    def run(self, packet):
        self.screen.fill(Color.BLACK.rgb())
        self.car_id = packet.car_id
        self.update_sprites(packet)
        self.update_rpm(self._normalize(packet.engine_rpm))
