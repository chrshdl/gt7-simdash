from hmi.color import Color
from hmi.widget import AbstractWidget


class Speedometer(AbstractWidget):
    def update(self, data):
        super().update(data)

        speed = str(int(data.car_speed * 3.6))
        speed = speed.center(len(speed))
        speed = self.primary_font.render(f"{speed}", False, Color.GREEN.rgb())
        res = tuple(map(sum, zip(self.image.get_rect().midbottom, (0, 4))))
        self.image.blit(speed, speed.get_rect(midbottom=res))
        label = self.recondary_font.render("Speed", False, Color.WHITE.rgb())
        midtop = tuple(map(sum, zip(self.image.get_rect().midtop, (0, 10))))
        self.image.blit(label, label.get_rect(midtop=midtop))
