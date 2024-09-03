import pygame
from granturismo.model import Packet

from hmi.properties import Color, TextAlignment
from hmi.settings import POS

from . import Widget


class Speedometer(Widget):
    def __init__(
        self, groups: pygame.sprite.Group, w: int, h: int, mfs: int = 124, hfs: int = 42
    ):
        super().__init__(groups, w, h, mfs, hfs)
        self.rect.center = POS["speed"]
        self.header_text = "Speed"
        self.body_text_color = Color.GREEN.rgb()
        self.body_text_alignment = TextAlignment.MIDBOTTOM

    def update(self, packet: Packet) -> None:  # type: ignore
        super().update(use_border=False)

        speed = f"{int(packet.car_speed * 3.6)}"
        self.body_text = speed.center(len(speed))
