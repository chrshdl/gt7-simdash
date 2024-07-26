from hmi.settings import *
from hmi.widget import Widget
from hmi.event import Event
from hmi.color import Color


class RPM(Widget):

    LED_OFF = 0
    LED_2_ON = 1
    LED_4_ON = 2
    LED_6_ON = 4
    LED_8_ON = 8

    def __init__(self, groups, w, h, main_fsize=28):
        super().__init__(groups, w, h, main_fsize)
        self.rect.center = POS["rpm"]

        self.LED_STATE = RPM.LED_OFF

        self.curr_rpm = 0
        self.alert_min = 7800
        self.alert_max = 8000
        self.delta = 1000
        self.delay = 0

    def update(self, dt, packet=None):
        super().update()

        # self.delay += dt

        self.curr_rpm = int(packet.engine_rpm)
        self.alert_min = packet.rpm_alert.min
        self.alert_max = packet.rpm_alert.max

        rpm_render = self.main_font.render(f"{self.curr_rpm}", False, Color.GREEN.rgb())
        self.image.blit(
            rpm_render, rpm_render.get_rect(center=rpm_render.get_rect().center)
        )

        if bool(self.LED_STATE | RPM.LED_OFF):
            if self.curr_rpm < self.alert_min - self.delta:
                self.LED_STATE = RPM.LED_OFF
                pygame.event.post(pygame.event.Event(Event.LEDS_CLEAR_ALL.type()))
        if not packet.flags.rev_limiter_alert_active:
            if self.curr_rpm in range(
                self.alert_min - self.delta, self.alert_min - self.delta // 2
            ):
                if not bool(self.LED_STATE & RPM.LED_2_ON):
                    pygame.event.post(
                        pygame.event.Event(Event.LEDS_SHOW.type(), message=2)
                    )
                    self.LED_STATE = RPM.LED_2_ON
            elif self.curr_rpm in range(
                self.alert_min - self.delta // 2, self.alert_min
            ):
                if not bool(self.LED_STATE & RPM.LED_4_ON):
                    pygame.event.post(
                        pygame.event.Event(Event.LEDS_SHOW.type(), message=4)
                    )
                    self.LED_STATE = RPM.LED_4_ON
            elif self.curr_rpm in range(self.alert_min, self.alert_max):
                if not bool(self.LED_STATE & RPM.LED_6_ON):
                    pygame.event.post(
                        pygame.event.Event(Event.LEDS_SHOW.type(), message=6)
                    )
                    self.LED_STATE = RPM.LED_6_ON
