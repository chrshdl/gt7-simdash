from hmi.settings import *
from hmi.color import Color
from hmi.widget import Widget


class GearIndicator(Widget):
    def __init__(self, groups, w, h, main_fsize=240):
        super().__init__(groups, w, h, main_fsize)
        self.rect.topleft = POS["gear"]

    def update(self, dt, packet):
        super().update()

        if not packet.flags.in_gear:
            gear = "N"
        else:
            if int(packet.current_gear) == 0:
                gear = "R"
            elif int(packet.current_gear) == None:
                gear = "N"
            else:
                gear = str(int(packet.current_gear))
        if packet.flags.rev_limiter_alert_active:
            color = Color.LIGHT_RED.rgb()
        else:
            color = Color.WHITE.rgb()
        gear_render = self.main_font.render(f"{gear}", False, color)
        self.image.blit(
            gear_render, gear_render.get_rect(center=self.image.get_rect().center)
        )
