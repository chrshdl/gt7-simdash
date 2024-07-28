from hmi.color import Color
from hmi.event import Event
import platform

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
        self.colors.append(Color.RED.rgb())
        self.colors.append(Color.RED.rgb())

    def draw(self, events):
        for e in events:
            if e.type == Event.HMI_RPM_LEDS_CHANGED.type():
                if platform.machine() == RASPBERRY_PI:
                    if e.message == 0:
                        self.clear_all()
                    else:
                        self.show(e.message)

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
        blinkt.show()
