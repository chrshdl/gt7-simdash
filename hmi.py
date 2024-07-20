import pygame
from color import Color
from speed import Speedometer
from gear import GearIndicator
from rpm import RPM
from lap import LastLap, BestLap
from mysprite import DebugSprite, InitializingSprite
from event import Event


class HMI:
    def __init__(self, rpm_min=1500, rpm_max=2000, car_id=-1):
        self._started = False
        self._car_id = car_id

        self.screen = pygame.display.get_surface()

        self.initializing = InitializingSprite(
            self.screen.get_size()[0], self.screen.get_size()[1], 0, 0
        )

        self.sprites = pygame.sprite.Group()
        self.sprites.add(Speedometer(180, 130, 310, 10))
        self.sprites.add(GearIndicator(180, 220, self.screen.get_size()[0] // 2, 350))
        self.sprites.add(LastLap(180, 88, 610, 10))
        self.sprites.add(BestLap(180, 88, 610, 372))
        self.sprites.add(DebugSprite(180, 88, 610, 270))

        self.rpm = pygame.sprite.Group()
        self.add_rpm(rpm_min, rpm_max)

    def add_rpm(self, rpm_min, rpm_max):
        y = 165

        rpm_min = self._normalize(rpm_min)
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
        print(f"car_id changed to: {self.car_id}")
        pygame.event.post(pygame.event.Event(Event.NEW_CAR_EVENT.name()))
        print(f"emitting NEW_CAR_EVENT")

    def _on_started(self):
        pygame.event.post(pygame.event.Event(Event.HMI_STARTED_EVENT.name()))
        print(f"emitting HMI_STARTED_EVENT")

    def draw_text(self, text):
        self.initializing.update(text)
        self.screen.blit(self.initializing.image, (0, 0))
        pygame.display.update()

    def run(self, packet):
        self.screen.fill(Color.BLACK.rgb())
        self.car_id = packet.car_id
        self.update_sprites(packet)
        self.update_rpm(self._normalize(packet.engine_rpm))
