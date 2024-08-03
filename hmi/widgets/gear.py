from . import Widget
from hmi.settings import POS
from hmi.properties import Color, TextAlignment


class GearIndicator(Widget):
    def __init__(self, groups, w, h, mfs=240):
        super().__init__(groups, w, h, mfs)
        self.rect.topleft = POS["gear"]
        self.body_text_alignment = TextAlignment.CENTER
        self.body_text_color = Color.WHITE.rgb()

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

        self.body_text_color = (
            Color.LIGHT_RED.rgb()
            if packet.flags.rev_limiter_alert_active
            else Color.WHITE.rgb()
        )
        self.body_text = f"{gear}"

