from hmi.settings import POS
from hmi.widget import Widget
from hmi.properties import Alignment


class Speedometer(Widget):
    def __init__(self, groups, w, h, main_fsize=108, header_fsize=46):
        super().__init__(groups, w, h, main_fsize, header_fsize)
        self.rect.center = POS["speed"]
        self.header_text = "Speed"
        self.body_alignment = Alignment.MIDBOTTOM

    def update(self, packet):
        super().update()

        speed = f"{int(packet.car_speed * 3.6)}"
        self.body_text = speed.center(len(speed))
