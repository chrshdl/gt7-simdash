from hmi.color import Color
from hmi.event import Event
import platform
import logging
import time

from logformatter import LogFormatter

if platform.machine() == "aarch64":
    import blinkt


class LED:
    def __init__(self):

        if platform.machine() == "aarch64":
            blinkt.set_brightness(0.1)

        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging.DEBUG)

        sh = logging.StreamHandler()
        sh.setLevel(logging.DEBUG)
        sh.setFormatter(LogFormatter())
        self.logger.addHandler(sh)
        self.colors = list()
        self.colors.append(Color.BLUE.rgb())
        self.colors.append(Color.GREEN.rgb())
        self.colors.append(Color.RED.rgb())
        self.colors.append(Color.RED.rgb())
        self.leds_to_set = 0

    def update(self, events):
        for e in events:
            if e.type == Event.LEDS_SHOW_ALL_RED.type():
                if platform.machine() == "aarch64":
                    self.show(e.message)

            if e.type == Event.LEDS_CLEAR_ALL.type():
                if platform.machine() == "aarch64":
                    self.leds_to_set = 0
                    blinkt.clear()
                    blinkt.show()

    def clear_all(self):
        self.logger.info("LEDS CLEARED")
        blinkt.clear()
        blinkt.show()

    def show(self, target):
        self.logger.info("LEDS ARE ACTIVE")
        if target == 10:
            if self.leds_to_set != target:
                self.leds_to_set = target
                blinkt.set_all(
                        self.colors[3][0],
                        self.colors[3][1],
                        self.colors[3][2]
                )
                blinkt.show()
        else:
            for i in range(target // 2):
                blinkt.set_pixel(i, self.colors[i][0], self.colors[i][1], self.colors[i][2])
                blinkt.set_pixel(
                    blinkt.NUM_PIXELS - 1 - i, self.colors[i][0], self.colors[i][1], self.colors[i][2]
                )
            blinkt.show()
