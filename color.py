from enum import Enum


class Color(Enum):
    GREEN = (1, (40, 90, 27))
    BLACK = (2, (0, 0, 0))
    RED = (3, (200, 0, 0))
    DARK_RED = (4, (90, 0, 0))
    GREY = (5, (40, 40, 40))
    DARK_GREY = (6, (10, 10, 10))
    LIGHT_GREY = (7, (120, 120, 120))
    BLUE = (8, (0, 120, 255))

    def rgb(self):
        return self.value[1]
