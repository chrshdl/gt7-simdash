import math
import pygame
from . import Widget
from hmi.settings import POS
from common.evendispatcher import EventDispatcher

from events import RACE_NEW_LAP_STARTED, RACE_RETRY_STARTED

SCALE_FACTOR = 6
DELTA = 0


class Minimap(Widget):
    def __init__(self, groups, w, h):
        super().__init__(groups, w, h)
        self.rect.center = POS["minimap"]
        self.px = None
        self.pz = None
        self.w = w
        self.h = h
        self.driven_distance = 0
        self.clear_map = False

        EventDispatcher.add_listener(RACE_NEW_LAP_STARTED, self.on_new_lap)
        EventDispatcher.add_listener(RACE_RETRY_STARTED, self.on_retry)

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
                self.px / SCALE_FACTOR + self.h // 2 + DELTA,
                self.pz / SCALE_FACTOR + self.h // 2 + DELTA,
            ],
            [
                x / SCALE_FACTOR + self.h // 2 + DELTA,
                z / SCALE_FACTOR + self.h // 2 + DELTA,
            ],
            SCALE_FACTOR - 2,
        )
        self.driven_distance += abs(x - self.px) * 1 / 60
        self.px = x
        self.pz = z

    def on_new_lap(self, event):
        print(f"lap: {event.data}, driven distance: {self.driven_distance / 10}")
        self.driven_distance = 0
        self.clear_map = False

    def on_retry(self, event):
        self.driven_distance = 0
        self.clear_map = True

    def colormap(self, f):
        """
        https://www.particleincell.com/2014/colormap/
        """
        a = (1 - f) / 0.2
        X = math.floor(a)
        Y = math.floor(255 * (a - X))
        match X:
            case 0:
                r = 255
                g = Y
                b = 0
            case 1:
                r = 255 - Y
                g = 255
                b = 0
            case 2:
                r = 0
                g = 255
                b = Y
            case 3:
                r = 0
                g = 255 - Y
                b = 255
            case 4:
                r = Y
                g = 0
                b = 255
            case 5:
                r = 255
                g = 0
                b = 255

        return (r, g, b)
