from hmi.settings import POS
from hmi.widget import Widget


class Speedometer(Widget):
    def __init__(self, groups, w, h, main_fsize=108, header_fsize=46):
        super().__init__(groups, w, h, main_fsize, header_fsize)
        self.rect.center = POS["speed"]
        self.header = "Speed"

    def update(self, packet):
        super().update()

        speed = f"{int(packet.car_speed * 3.6)}"
        self.value = speed.center(len(speed))
