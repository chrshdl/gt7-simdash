from enum import Enum


class Color(Enum):
    GREEN = (1, (40, 90, 27))
    BLACK = (2, (0, 0, 0))
    RED = (3, (200, 0, 0))
    DARK_RED = (4, (90, 0, 0))
    GREY = (5, (20, 20, 20))
    DARK_GREY = (6, (10, 10, 10))
    BLUE = (7, (0, 120, 255))

    def rgb(self):
        return self.value[1]
