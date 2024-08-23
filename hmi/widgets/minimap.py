import numpy as np
import pygame

from common.evendispatcher import EventDispatcher
from events import RACE_NEW_LAP_STARTED, RACE_RETRY_STARTED
from hmi.properties import Color
from hmi.settings import CIRCUITS, POS

from . import Widget


class Minimap(Widget):
    def __init__(self, groups, w, h):
        super().__init__(groups, w, h)
        self.rect.topleft = POS["minimap"]
        self.px = None
        self.pz = None
        self.w = w
        self.h = h
        self.driven_distance = 0
        circuit_name = "goodwood"  # TODO: infer circuit_name from the data
        self.clear_map = False
        self.MAP_SCALE = self.w / 5
        self.LINE_SCALE = 6
        self.DELTA = self.w / 2
        mean_x = CIRCUITS[circuit_name]["mean"][0]
        mean_z = CIRCUITS[circuit_name]["mean"][1]
        std_x = CIRCUITS[circuit_name]["std"][0]
        std_z = CIRCUITS[circuit_name]["std"][1]
        self.M = np.array([[1, 0], [0, 1], [-mean_x, -mean_z]])
        self.norm = np.array([std_x, std_z])

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

        speed = (
            min(1, packet.car_speed / packet.car_max_speed) * 2
            if packet.car_max_speed > 0
            else 0
        )
        prv_pos = (np.dot(np.array([self.px, self.pz, 1]), self.M) / self.norm).tolist()
        cur_pos = (np.dot(np.array([x, z, 1]), self.M) / self.norm).tolist()

        pygame.draw.line(
            self.image,
            Color.colormap(speed),
            [
                self.MAP_SCALE * prv_pos[0] + self.DELTA,
                self.MAP_SCALE * prv_pos[1] + self.DELTA,
            ],
            [
                self.MAP_SCALE * cur_pos[0] + self.DELTA,
                self.MAP_SCALE * cur_pos[1] + self.DELTA,
            ],
            self.LINE_SCALE,
        )

        self.driven_distance += self.compute_l2_norm(x, z, self.px, self.pz)

        self.px = x
        self.pz = z

    def on_new_lap(self, event):
        print(f"lap: {event.data - 1}, driven: {self.driven_distance * 1e-3:.3f} km")
        self.driven_distance = 0
        self.clear_map = False

    def on_retry(self, event):
        self.driven_distance = 0
        self.clear_map = True

    def compute_l2_norm(self, x, z, px, pz):
        return np.linalg.norm(np.array([x, z]) - np.array([px, pz]))
