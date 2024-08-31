import numpy as np
import pygame

from hmi.properties import Color
from hmi.settings import CIRCUITS, POS

from . import Widget


class Carsor(Widget):
    def __init__(self, groups, w, h):
        super().__init__(groups, w, h)
        self.rect.topleft = POS["minimap"]
        self.w = w
        self.h = h
        self.image = pygame.Surface((w, h), pygame.SRCALPHA).convert_alpha()
        circuit_name = "Nordschleife"  # TODO: infer circuit_name from the data
        self.MAP_SCALE = self.w / 6
        self.LINE_SCALE = 8
        self.DELTA = self.w / 2
        mean_x = CIRCUITS[circuit_name]["mean"][0]
        mean_z = CIRCUITS[circuit_name]["mean"][1]
        std_x = CIRCUITS[circuit_name]["std"][0]
        std_z = CIRCUITS[circuit_name]["std"][1]
        self.M = np.array([[1, 0], [0, 1], [-mean_x, -mean_z]])
        self.norm = np.array([std_x, std_z])

    def update(self, packet):
        super().update(use_border=False)

        x, z = packet.position.x, packet.position.z

        car_pos = np.dot(np.array([x, z, 1]), self.M) / self.norm

        pygame.draw.circle(
            self.image,
            Color.LIGHT_RED.rgb(),
            [
                self.MAP_SCALE * car_pos[0] + self.DELTA,
                self.MAP_SCALE * car_pos[1] + self.DELTA,
            ],
            self.LINE_SCALE,
        )
        pygame.draw.circle(
            self.image,
            Color.DARK_RED.rgb(),
            [
                self.MAP_SCALE * car_pos[0] + self.DELTA,
                self.MAP_SCALE * car_pos[1] + self.DELTA,
            ],
            self.LINE_SCALE,
            3,
        )
