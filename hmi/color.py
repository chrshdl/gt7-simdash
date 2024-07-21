from enum import Enum


class Color(Enum):
    GREEN = (1, (0, 200, 0))
    BLACK = (2, (0, 0, 0))
    LIGHT_RED = (3, (250, 50, 50))
    RED = (4, (200, 0, 0))
    DARK_RED = (5, (90, 0, 0))
    GREY = (6, (40, 40, 40))
    DARK_GREY = (7, (5, 5, 5))
    LIGHT_GREY = (8, (120, 120, 120))
    BLUE = (9, (0, 120, 255))
    WHITE = (10, (210, 210, 210))

    def rgb(self):
        return self.value[1]
