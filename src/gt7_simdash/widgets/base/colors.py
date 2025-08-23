import math
from enum import Enum, auto
from typing import Union

RGB = tuple[int, int, int]
RGBA = tuple[int, int, int, int]
ColorValues = Union[RGB, RGBA]


class Color(Enum):
    GREEN = (auto(), (0, 200, 0))
    DARK_GREEN = (auto(), (18, 136, 54))
    LIGHT_GREEN = (auto(), (80, 255, 120))
    YELLOW = (auto(), (200, 200, 0))
    DARK_YELLOW = (auto(), (136, 136, 0))
    BLACK = (auto(), (0, 0, 0, 10))
    LIGHT_RED = (auto(), (250, 50, 50))
    LIGHTEST_RED = (auto(), (255, 80, 80))
    RED = (auto(), (200, 0, 0))
    DARK_RED = (auto(), (140, 30, 30))
    RPM_RED = (auto(), (225, 0, 45))
    RPM_DARK_RED = (auto(), (175, 30, 30))
    GREY = (auto(), (40, 40, 40))
    MEDIUM_GREY = (auto(), (10, 20, 30))
    DARK_GREY = (auto(), (30, 30, 30))
    LIGHT_GREY = (auto(), (120, 120, 120))
    BLUE = (auto(), (0, 120, 255))
    DARK_BLUE = (auto(), (0, 50, 125))
    DARKEST_BLUE = (auto(), (0, 3, 10))
    WHITE = (auto(), (210, 210, 210))
    PURPLE = (auto(), (200, 0, 200))
    LIGHT_PURPLE = (auto(), (185, 35, 135))
    MEDIUM_PURPLE = (auto(), (125, 50, 140))
    DEEP_PURPLE = (auto(), (90, 10, 165))

    def rgb(self) -> ColorValues:
        return self.value[1]

    @classmethod
    def colormap(cls, f: float) -> ColorValues:
        """
        https://www.particleincell.com/2014/colormap/
        """
        a = (1 - f) * 5
        X = math.floor(a)
        Y = math.floor(255 * (a - X))
        match X:
            case 0:
                return (255, Y, 0)
            case 1:
                return (255 - Y, 255, 0)
            case 2:
                return (0, 255, Y)
            case 3:
                return (0, 255 - Y, 255)
            case 4:
                return (Y, 0, 255)
            case 5:
                return cls.PURPLE.rgb()
        raise NotImplementedError(f"colormap does not support input {f} yet.")
