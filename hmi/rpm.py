from hmi.settings import *
from hmi.widget import Widget
from hmi.event import Event


class RPM(Widget):
    def __init__(self, groups, w, h):
        super().__init__(groups, w, h)
        self.rect.center = POS["rpm"]

        self.led_active = False
        self.curr_rpm = 0
        self.alert_min = 7800
        self.alert_max = 8000
        self.delta = 200
        self.delay = 0

    def update(self, dt, packet=None):
        super().update()

        self.delay += dt

        self.curr_rpm = int(packet.engine_rpm)
        self.alert_min = packet.rpm_alert.min
        self.alert_max = packet.rpm_alert.max

        if self.led_active:
            if self.curr_rpm < self.alert_min - self.delta:
                self.led_active = False
                pygame.event.post(pygame.event.Event(Event.LEDS_CLEAR_ALL.type()))
    
        if self.delay > 0.08:
            self.delay = 0
            if self.curr_rpm in range(self.alert_min - self.delta, self.alert_min):
                self.led_active = True
                pygame.event.post(
                    pygame.event.Event(Event.LEDS_SHOW.type(), message=2)
                )
            elif self.curr_rpm in range(self.alert_min, self.alert_min + self.delta):
                self.led_active = True
                pygame.event.post(
                    pygame.event.Event(Event.LEDS_SHOW.type(), message=4)
                )
            elif self.curr_rpm > self.alert_max:
                self.led_active = True
                pygame.event.post(
                    pygame.event.Event(Event.LEDS_SHOW.type(), message=6)
                )

