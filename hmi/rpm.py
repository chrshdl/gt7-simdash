from hmi.settings import *
from hmi.widget import Widget
from hmi.event import Event
from hmi.color import Color
import logging

from logformatter import LogFormatter


class RPM(Widget):

    LED_OFF = 0
    LED_2_ON = 2
    LED_4_ON = 4
    LED_8_ON = 8

    def __init__(self, groups, w, h, main_fsize=28):
        super().__init__(groups, w, h, main_fsize)
        self.rect.center = POS["rpm"]

        self._led_state = RPM.LED_OFF

        self.curr_rpm = 0
        self._alert_min = 0
        self._alert_max = 0
        self.delta = 1000

        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging.DEBUG)

        sh = logging.StreamHandler()
        sh.setLevel(logging.DEBUG)
        sh.setFormatter(LogFormatter())
        self.logger.addHandler(sh)

    def update(self, dt, packet=None):
        super().update()

        curr_rpm = int(packet.engine_rpm)
        limiter_active = packet.flags.rev_limiter_alert_active

        rpm_render = self.main_font.render(f"{curr_rpm}", False, Color.GREEN.rgb())
        self.image.blit(
            rpm_render, rpm_render.get_rect(center=rpm_render.get_rect().center)
        )

        self.update_leds(curr_rpm, limiter_active)

    def update_leds(self, curr_rpm, limiter_active):
        if bool(self._led_state | RPM.LED_OFF):
            if curr_rpm < self._alert_min - self.delta:
                self.led(RPM.LED_OFF)
        if not limiter_active:
            if curr_rpm in range(
                self._alert_min - self.delta, self._alert_min - self.delta // 2
            ):
                if not bool(self._led_state & RPM.LED_2_ON):
                    self.led(RPM.LED_2_ON)
            elif curr_rpm in range(self._alert_min - self.delta // 2, self._alert_min):
                if not bool(self._led_state & RPM.LED_4_ON):
                    self.led(RPM.LED_4_ON)
            elif curr_rpm in range(self._alert_min, self._alert_max):
                if not bool(self._led_state & RPM.LED_8_ON):
                    self.led(RPM.LED_8_ON)

    def led(self, state):
        if self._led_state != state:
            self._led_state = state
            pygame.event.post(
                pygame.event.Event(
                    Event.HMI_RPM_LEDS_CHANGED.type(), message=self._led_state
                )
            )

    def alert_min(self, value):
        self._alert_min = value
        self.logger.info(f"RPM_ALERT.MIN is now: {self._alert_min}")

    def alert_max(self, value):
        self._alert_max = value
        self.logger.info(f"RPM_ALERT.MAX is now: {self._alert_max}")
