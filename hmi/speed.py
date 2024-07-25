from hmi.settings import *
from hmi.color import Color
from hmi.widget import Widget
from hmi.event import Event


class Speedometer(Widget):
    def __init__(self, groups, w, h, main_fsize=108, header_fsize=46):
        super().__init__(groups, w, h, main_fsize, header_fsize)
        self.rect.topleft = POS["speed"]
        self.car_speed = 0
        self.led_active = False

    def update(self, dt, packet=None):
        super().update()

        if packet is not None:
            self.car_speed = packet.car_speed * 3.6
        else:
            self.car_speed = (self.car_speed + (dt * 25)) % 400

        if self.led_active:
            if self.car_speed < 60:
                self.led_active = False
                pygame.event.post(pygame.event.Event(Event.LEDS_CLEAR_ALL.type()))
        else:
            if self.car_speed > 65 and self.car_speed < 75:
                self.led_active = True
                pygame.event.post(
                    pygame.event.Event(Event.LEDS_SHOW_ALL_RED.type(), message=2)
                )
            elif self.car_speed > 76 and self.car_speed < 90:
                self.led_active = True
                pygame.event.post(
                    pygame.event.Event(Event.LEDS_SHOW_ALL_RED.type(), message=4)
                )

        speed = str(int(self.car_speed))
        speed = speed.center(len(speed))
        speed = self.main_font.render(f"{speed}", False, Color.GREEN.rgb())
        res = tuple(map(sum, zip(self.image.get_rect().midbottom, (0, 4))))
        self.image.blit(speed, speed.get_rect(midbottom=res))
        label = self.header_font.render("Speed", False, Color.WHITE.rgb())
        midtop = tuple(map(sum, zip(self.image.get_rect().midtop, (0, 10))))
        self.image.blit(label, label.get_rect(midtop=midtop))
