import math
import numpy as np
import pygame
from . import Widget
from hmi.settings import POS, CIRCUITS
from common.evendispatcher import EventDispatcher

from events import RACE_NEW_LAP_STARTED, RACE_RETRY_STARTED


class Minimap(Widget):
    def __init__(self, groups, w, h):
        super().__init__(groups, w, h)
        self.rect.topleft = POS["minimap"]
        self.px = None
        self.pz = None
        self.w = w
        self.h = h
        self.driven_distance = 0
        circuit_name = "brands-hatch-indy"  # TODO: infer circuit_name from the data
        self.clear_map = False
        self.MAP_SCALE = self.w / 5
        self.LINE_SCALE = 2
        self.DELTA = self.w / 2
        self.mean_x = CIRCUITS[circuit_name]["mean"][0]
        self.mean_z = CIRCUITS[circuit_name]["mean"][1]
        self.std_x = CIRCUITS[circuit_name]["std"][0]
        self.std_z = CIRCUITS[circuit_name]["std"][1]

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
                (self.MAP_SCALE * ((self.px - self.mean_x) / self.std_x)) + self.DELTA,
                (self.MAP_SCALE * ((self.pz - self.mean_z) / self.std_z)) + self.DELTA,
            ],
            [
                (self.MAP_SCALE * ((x - self.mean_x) / self.std_x)) + self.DELTA,
                (self.MAP_SCALE * ((z - self.mean_z) / self.std_z)) + self.DELTA,
            ],
            self.LINE_SCALE,
        )
        self.driven_distance += np.linalg.norm(
            np.array([x, z]) - np.array([self.px, self.pz])
        )
        self.px = x
        self.pz = z

    def on_new_lap(self, event):
        print(
            f"lap: {event.data}, driven distance: {self.driven_distance * 1e-3:.3f} km"
        )
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
