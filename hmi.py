import pygame
from color import Color
from speed import Speedometer
from gear import GearIndicator
from rpm import RPM
from lap import LastLap, BestLap
from mysprite import DebugSprite
from event import Event


class HMI:
    def __init__(self, car_id, rpm_min, rpm_max):
        self.screen = pygame.display.get_surface()
        self.sprites = pygame.sprite.Group()
        self.sprites.add(Speedometer(180, 120, 310, 10))
        self.sprites.add(GearIndicator(180, 220, self.screen.get_size()[0] // 2, 350))
        self.sprites.add(LastLap(180, 88, 610, 10))
        self.sprites.add(BestLap(180, 88, 610, 120))
        self.sprites.add(DebugSprite(180, 88, 610, 230, 26))

        self._car_id = car_id

        self.rpm = pygame.sprite.Group()
        self.add_rpm(rpm_min, rpm_max)

    def add_rpm(self, rpm_min, rpm_max):
        y = 158

        rpm_min = int(rpm_min - rpm_max * 0.04) // 100
        rpm_max = self._normalize(rpm_max)

        screen_width = self.screen.get_size()[0]
        self.rpm.add(
            RPM(screen_width, y, rpm_min, rpm_max, step) for step in range(rpm_max + 1)
        )

    def _normalize(self, rpm):
        return int(rpm * 0.01) + 10

    def refresh_rpm(self, rpm_min, rpm_max):
        self.remove_all_rpm()
        self.add_rpm(rpm_min, rpm_max)

    def remove_all_rpm(self):
        for item in self.rpm:
            self.rpm.remove(item)

    def update_rpm(self, packet):
        self.rpm.update(packet)
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
            self.on_car_id_change()

    def on_car_id_change(self):
        print(f"car_id changed to: {self.car_id}")
        pygame.event.post(pygame.event.Event(Event.NEW_CAR_EVENT.name()))
        print(f"emmiting NEW_CAR_EVENT")

    def run(self, packet):
        self.screen.fill(Color.BLACK.rgb())
        self.car_id = packet.car_id
        self.update_sprites(packet)
        self.update_rpm(int(packet.engine_rpm) // 100)
