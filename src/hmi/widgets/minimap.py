from typing import Optional

import numpy as np
import pygame
from granturismo.model import Packet

from common.event import Event
from common.eventdispatcher import EventDispatcher
from events import RACE_NEW_LAP_STARTED, RACE_RETRY_STARTED
from hmi.properties import Color
from hmi.settings import CIRCUITS, POS

from . import Widget


class Minimap(Widget):
    def __init__(
        self, groups: pygame.sprite.Group, w: int, h: int, mfs: int = 40, hfs: int = 42
    ):
        super().__init__(groups, w, h, mfs, hfs)
        self.rect.topleft = POS["minimap"]
        self.px: Optional[float] = None
        self.pz: Optional[float] = None
        self.w: int = w
        self.h: int = h
        self.driven_distance = 0
        circuit_name: str = "Goodwood"  # TODO: infer circuit_name from the data
        self.header_text = circuit_name
        self.clear_map: bool = False
        self.MAP_SCALE: float = self.w / 6
        self.LINE_SCALE: int = 5
        self.DELTA: float = self.w / 2
        mean_x = CIRCUITS[circuit_name]["mean"][0]
        mean_z = CIRCUITS[circuit_name]["mean"][1]
        std_x = CIRCUITS[circuit_name]["std"][0]
        std_z = CIRCUITS[circuit_name]["std"][1]
        self.M: np.ndarray = np.array([[1, 0], [0, 1], [-mean_x, -mean_z]])
        self.norm: np.ndarray = np.array([std_x, std_z])

        EventDispatcher.add_listener(RACE_NEW_LAP_STARTED, self.on_new_lap)
        EventDispatcher.add_listener(RACE_RETRY_STARTED, self.on_retry)

    def update(self, packet: Packet) -> None:  # type:ignore
        if self.clear_map:
            super().update(use_border=False)
            self.clear_map = False

        x, z = packet.position.x, packet.position.z

        if self.px is None:
            self.px, self.pz = x, z
            return

        speed = (
            min(1, packet.car_speed / packet.car_max_speed) * 2
            if packet.car_max_speed
            else 0
        )
        prv_pos = np.dot(np.array([self.px, self.pz, 1]), self.M) / self.norm
        cur_pos = np.dot(np.array([x, z, 1]), self.M) / self.norm

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

        self.driven_distance += self.compute_l2_norm(x, z, self.px, self.pz)  # type: ignore

        self.px = x
        self.pz = z

    def on_new_lap(self, event: Event[int]) -> None:
        print(f"lap: {event.data - 1}, driven: {self.driven_distance * 1e-3:.3f} km")
        self.driven_distance = 0
        self.clear_map = False

    def on_retry(self, _) -> None:
        self.driven_distance = 0
        self.clear_map = True

    def compute_l2_norm(self, x: float, z: float, px: float, pz: float):
        return np.linalg.norm(np.array([x, z]) - np.array([px, pz]))
