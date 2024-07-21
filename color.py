from enum import Enum


class Color(Enum):
    GREEN = (1, (0, 200, 0))
    BLACK = (2, (0, 0, 0))
    RED = (3, (200, 0, 0))
    DARK_RED = (4, (90, 0, 0))
    GREY = (5, (40, 40, 40))
    DARK_GREY = (6, (5, 5, 5))
    LIGHT_GREY = (7, (120, 120, 120))
    BLUE = (8, (0, 120, 255))
    WHITE = (9, (210, 210, 210))

    def rgb(self):
        return self.value[1]
