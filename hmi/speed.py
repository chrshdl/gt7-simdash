from hmi.settings import *
from hmi.color import Color
from hmi.widget import Widget


class Speedometer(Widget):
    def __init__(self, groups, w, h, main_fsize=108, header_fsize=46):
        super().__init__(groups, w, h, main_fsize, header_fsize)
        self.rect.center = POS["speed"]
        self.car_speed = 0

    def update(self, dt, packet=None):
        super().update()

        self.car_speed = packet.car_speed * 3.6

        speed = str(int(self.car_speed))
        speed = speed.center(len(speed))
        speed = self.main_font.render(f"{speed}", False, Color.GREEN.rgb())
        res = tuple(map(sum, zip(self.image.get_rect().midbottom, (0, 4))))
        self.image.blit(speed, speed.get_rect(midbottom=res))
        label = self.header_font.render("Speed", False, Color.WHITE.rgb())
        midtop = tuple(map(sum, zip(self.image.get_rect().midtop, (0, 10))))
        self.image.blit(label, label.get_rect(midtop=midtop))
