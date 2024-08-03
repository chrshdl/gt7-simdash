from enum import Enum, auto


class Color(Enum):
    GREEN = (auto(), (0, 200, 0))
    BLACK = (auto(), (0, 0, 0))
    LIGHT_RED = (auto(), (250, 50, 50))
    RED = (auto(), (200, 0, 0))
    DARK_RED = (auto(), (90, 0, 0))
    GREY = (auto(), (40, 40, 40))
    DARK_GREY = (auto(), (5, 5, 5))
    LIGHT_GREY = (auto(), (120, 120, 120))
    BLUE = (auto(), (0, 120, 255))
    WHITE = (auto(), (210, 210, 210))

    def rgb(self):
        return self.value[1]


class TextAlignment(Enum):
    CENTER = (auto(), "center")
    MIDBOTTOM = (auto(), "midbottom")

    def type(self):
        return self.value[1]

