import math
from enum import Enum, auto


class Color(Enum):
    GREEN = (auto(), (0, 200, 0))
    DARK_GREEN = (auto(), (18, 136, 54))
    BLACK = (auto(), (0, 0, 0))
    LIGHT_RED = (auto(), (250, 50, 50))
    RED = (auto(), (200, 0, 0))
    DARK_RED = (auto(), (90, 0, 0))
    GREY = (auto(), (40, 40, 40))
    DARK_GREY = (auto(), (30, 30, 30))
    LIGHT_GREY = (auto(), (120, 120, 120))
    BLUE = (auto(), (0, 120, 255))
    DARK_BLUE = (auto(), (0, 50, 124))
    DARKEST_BLUE = (auto(), (0, 3, 8))
    WHITE = (auto(), (210, 210, 210))
    PURPLE = (auto(), (200, 0, 200))

    def rgb(self):
        return self.value[1]

    @classmethod
    def colormap(cls, f):
        """
        https://www.particleincell.com/2014/colormap/
        """
        a = (1 - f) / 0.2
        X = math.floor(a)
        Y = math.floor(255 * (a - X))
        match X:
            case 0:
                r = 255
                g = Y
                b = 0
            case 1:
                r = 255 - Y
                g = 255
                b = 0
            case 2:
                r = 0
                g = 255
                b = Y
            case 3:
                r = 0
                g = 255 - Y
                b = 255
            case 4:
                r = Y
                g = 0
                b = 255
            case 5:
                r, g, b = cls.PURPLE.rgb()

        return (r, g, b)


class TextAlignment(Enum):
    CENTER = (auto(), "center")
    MIDBOTTOM = (auto(), "midbottom")

    def type(self):
        return self.value[1]
