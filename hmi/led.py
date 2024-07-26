from hmi.color import Color
from hmi.event import Event
import platform
import logging

from logformatter import LogFormatter

RASPBERRY_PI = "aarch64"
if platform.machine() == RASPBERRY_PI:
    import blinkt


class LED:
    def __init__(self):

        if platform.machine() == RASPBERRY_PI:
            blinkt.set_brightness(0.05)

        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging.DEBUG)

        sh = logging.StreamHandler()
        sh.setLevel(logging.DEBUG)
        sh.setFormatter(LogFormatter())
        self.logger.addHandler(sh)
        self.colors = list()
        self.colors.append(Color.BLUE.rgb())
        self.colors.append(Color.BLUE.rgb())
        self.colors.append(Color.GREEN.rgb())
        self.colors.append(Color.GREEN.rgb())

    def draw(self, events):
        for e in events:
            if e.type == Event.LEDS_SHOW.type():
                if platform.machine() == RASPBERRY_PI:
                    self.show(e.message)

            if e.type == Event.LEDS_CLEAR_ALL.type():
                if platform.machine() == RASPBERRY_PI:
                    blinkt.clear()
                    blinkt.show()

    def clear_all(self):
        # self.logger.info("LEDS CLEARED")
        blinkt.clear()
        blinkt.show()

    def show(self, target):
        # self.logger.info(f"LEDS ARE ACTIVE: {target}")
        for i in range(target // 2):
            blinkt.set_pixel(i, self.colors[i][0], self.colors[i][1], self.colors[i][2])
            blinkt.set_pixel(
                blinkt.NUM_PIXELS - 1 - i,
                self.colors[i][0],
                self.colors[i][1],
                self.colors[i][2],
            )
        blinkt.show()
