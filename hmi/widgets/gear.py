from typing import Union

import pygame
from granturismo.model import Packet

from hmi.properties import Color, TextAlignment
from hmi.settings import POS

from . import Widget


class GearIndicator(Widget):
    def __init__(self, groups: pygame.sprite.Group, w: int, h: int, mfs: int = 300):
        super().__init__(groups, w, h, mfs)
        self.rect.center = POS["gear"]
        self.body_text_alignment = TextAlignment.CENTER
        self.body_text_color = Color.WHITE.rgb()

    def update(self, packet: Packet) -> None:  # type: ignore
        super().update(use_gradient=False)

        if not packet.flags.in_gear:
            gear: Union[str, int] = "N"
        else:
            if int(packet.current_gear) == 0:
                gear = "R"
            elif packet.current_gear is None:
                gear = "N"
            else:
                gear = int(packet.current_gear)

        self.body_text_color = (
            Color.LIGHT_RED.rgb()
            if packet.flags.rev_limiter_alert_active
            else Color.WHITE.rgb()
        )
        self.body_text = f"{gear}"
