from hmi.settings import POS
from hmi.properties import Color, Alignment
from hmi.widget import Widget


class GearIndicator(Widget):
    def __init__(self, groups, w, h, main_fsize=240):
        super().__init__(groups, w, h, main_fsize)
        self.rect.topleft = POS["gear"]
        self.body_alignment = Alignment.CENTER

    def update(self, packet):
        super().update()

        if not packet.flags.in_gear:
            gear = "N"
        else:
            if int(packet.current_gear) == 0:
                gear = "R"
            elif packet.current_gear == None:
                gear = "N"
            else:
                gear = int(packet.current_gear)

        self.body_color = (
            Color.LIGHT_RED.rgb()
            if packet.flags.rev_limiter_alert_active
            else Color.WHITE.rgb()
        )
        self.body_text = f"{gear}"
