from . import Widget
from hmi.settings import POS
from hmi.properties import TextAlignment


class Speedometer(Widget):
    def __init__(self, groups, w, h, mfs=108):
        super().__init__(groups, w, h, mfs)
        self.rect.center = POS["speed"]
        self.header_text = "Speed"
        self.body_text_alignment = TextAlignment.MIDBOTTOM

    def update(self, packet):
        super().update()

        speed = f"{int(packet.car_speed * 3.6)}"
        self.body_text = speed.center(len(speed))
