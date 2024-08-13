import math
import pygame
from common.evendispatcher import EventDispatcher
from events import RACE_NEW_LAP_STARTED, RACE_NEW_TRY_STARTED
from . import Widget
from hmi.settings import POS

SCALE_FACTOR = 6


class Minimap(Widget):
    def __init__(self, groups, w, h, mfs=300):
        super().__init__(groups, w, h, mfs)
        self.rect.center = POS["map"]
        self.px = None
        self.pz = None
        self.w = w
        self.h = h
        self.driven_distance = 0
        self.clear_map = False

        EventDispatcher.add_listener(RACE_NEW_LAP_STARTED, self.on_new_lap_started)
        EventDispatcher.add_listener(RACE_NEW_TRY_STARTED, self.on_new_try_started)

    def update(self, packet):
        if self.clear_map:
            super().update(use_border=False)
            self.clear_map = False

        x, z = packet.position.x, packet.position.z
        if self.px is None:
            self.px, self.pz = x, z
            return

        if packet.car_max_speed > 0:
            speed = min(1, packet.car_speed / packet.car_max_speed) * 2
        else:
            speed = 0

        pygame.draw.line(
            self.image,
            self.colormap(speed),
            [
                self.px / SCALE_FACTOR + self.w // 2,
                self.pz / SCALE_FACTOR + self.w // 2,
            ],
            [x / SCALE_FACTOR + self.h // 2, z / SCALE_FACTOR + self.h // 2],
            SCALE_FACTOR,
        )
        self.driven_distance += abs(x - self.px) * 1 / 60
        self.px = x
        self.pz = z

    def on_new_lap_started(self, event):
        print(f"lap: {event.data}, driven distance: {self.driven_distance / 10}")
        self.driven_distance = 0
        self.clear_map = False

    def on_new_try_started(self, event):
        self.driven_distance = 0
        self.clear_map = True

    def colormap(self, f):
        """
        https://www.particleincell.com/2014/colormap/
        """
        a = 1 - f
        Y = math.floor(255 * a)

        r = 255 - Y
        g = 0
        b = 255

        return (r, g, b)
