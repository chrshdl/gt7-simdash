import pygame
from hmi.settings import POS
from hmi.widget import Widget
from hmi.event import Event
from hmi.properties import Alignment


class RPM(Widget):

    LED_OFF = 0
    LED_2_ON = 2
    LED_4_ON = 4
    LED_8_ON = 8

    def __init__(self, groups, w, h, main_fsize=28):
        super().__init__(groups, w, h, main_fsize)
        self.rect.center = POS["rpm"]
        self.body_alignment = Alignment.CENTER

        self._led_state = RPM.LED_OFF

        self.curr_rpm = 0
        self._alert_min = 6000
        self._alert_max = 7000
        self.delta = 1000

        self.RPM_LEVEL_0 = self._alert_min - self.delta
        self.RPM_LEVEL_1 = self.RPM_LEVEL_0 // 2
        self.RPM_LEVEL_2 = self._alert_min
        self.RPM_LEVEL_3 = self._alert_max

    def update(self, packet):
        super().update()

        curr_rpm = int(packet.engine_rpm)
        limiter_active = packet.flags.rev_limiter_alert_active

        self.body_text = f"{curr_rpm}"

        self.update_leds(curr_rpm, limiter_active)

    def update_leds(self, curr_rpm, limiter_active):
        if bool(self._led_state | RPM.LED_OFF):
            if curr_rpm < self.RPM_LEVEL_0:
                self.led(RPM.LED_OFF)
        if not limiter_active:
            if curr_rpm in range(self.RPM_LEVEL_0, self.RPM_LEVEL_1):
                if not bool(self._led_state & RPM.LED_2_ON):
                    self.led(RPM.LED_2_ON)
            elif curr_rpm in range(self.RPM_LEVEL_1, self.RPM_LEVEL_2):
                if not bool(self._led_state & RPM.LED_4_ON):
                    self.led(RPM.LED_4_ON)
            elif curr_rpm in range(self.RPM_LEVEL_2, self.RPM_LEVEL_3):
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

    def alert_max(self, value):
        self._alert_max = value
