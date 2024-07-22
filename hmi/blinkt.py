import blinkt
import time
from hmi.color import Color


colors = list()


def init():
    colors.append(Color.BLUE.rgb())
    colors.append(Color.GREEN.rgb())
    colors.append(Color.GREEN.rgb())
    colors.append(Color.RED.rgb())
    blinkt.set_brightness(0.05)
    clear_all()


def clear_all():
    blinkt.clear()
    blinkt.show()


if __name__ == "__main__":

    init()

    while True:
        for i in range(blinkt.NUM_PIXELS // 2):
            blinkt.set_pixel(i, colors[i][0], colors[i][1], colors[i][2])
            blinkt.set_pixel(
                blinkt.NUM_PIXELS - 1 - i, colors[i][0], colors[i][1], colors[i][2]
            )
            blinkt.show()
            time.sleep(0.5)

        for _ in range(4):
            clear_all()
            for i in range(blinkt.NUM_PIXELS // 2):
                blinkt.set_pixel(i, colors[i][0], colors[i][1], colors[i][2])
                blinkt.set_pixel(
                    blinkt.NUM_PIXELS - 1 - i, colors[i][0], colors[i][1], colors[i][2]
                )
            blinkt.show()
            time.sleep(0.05)
        clear_all()
