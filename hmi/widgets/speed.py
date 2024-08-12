from . import Widget
from hmi.settings import POS
from hmi.properties import Color, TextAlignment


class Speedometer(Widget):
    def __init__(self, groups, w, h, mfs=124, hfs=42):
        super().__init__(groups, w, h, mfs, hfs)
        self.rect.center = POS["speed"]
        self.header_text = "Speed"
        self.body_text_color = Color.GREEN.rgb()
        self.body_text_alignment = TextAlignment.MIDBOTTOM

    def update(self, packet):
        super().update(use_border=False)

        speed = f"{int(packet.car_speed * 3.6)}"
        self.body_text = speed.center(len(speed))
