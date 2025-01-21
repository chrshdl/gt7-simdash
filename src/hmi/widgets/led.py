import platform

from events import HMI_RPM_LEVEL_CHANGED
from hmi.properties import Color

from . import EventDispatcher, Logger

RASPBERRY_PI = "aarch64"
if platform.machine() == RASPBERRY_PI:
    import blinkt


class LED:
    def __init__(self):
        if platform.machine() == RASPBERRY_PI:
            blinkt.set_brightness(0.05)

        self.colors = list()
        self.colors.append(Color.BLUE.rgb())
        self.colors.append(Color.BLUE.rgb())
        self.colors.append(Color.GREEN.rgb())
        self.colors.append(Color.RED.rgb())

        self.logger = Logger(self.__class__.__name__).get()

        EventDispatcher.add_listener(HMI_RPM_LEVEL_CHANGED, self.on_rpm_changed)

    def on_rpm_changed(self, event):
        if event.data == 0:
            self.logger.info("clear all LEDs")
            if platform.machine() == RASPBERRY_PI:
                self.clear_all()
        else:
            self.logger.info(f"show {event.data} LEDs")
            if platform.machine() == RASPBERRY_PI:
                self.show(event.data)

    def clear_all(self):
        blinkt.clear()
        blinkt.show()

    def show(self, target):
        for i in range(target // 2):
            blinkt.set_pixel(i, self.colors[i][0], self.colors[i][1], self.colors[i][2])
            blinkt.set_pixel(
                blinkt.NUM_PIXELS - 1 - i,
                self.colors[i][0],
                self.colors[i][1],
                self.colors[i][2],
            )
        for i in range(target // 2, blinkt.NUM_PIXELS // 2):
            blinkt.set_pixel(i, 0, 0, 0)
            blinkt.set_pixel(blinkt.NUM_PIXELS - 1 - i, 0, 0, 0)
        blinkt.show()
