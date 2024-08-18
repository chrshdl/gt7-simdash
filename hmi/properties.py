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
    WHITE_OPACITY = (auto(), (210, 210, 210, 80))

    def rgb(self):
        return self.value[1]


class TextAlignment(Enum):
    CENTER = (auto(), "center")
    MIDBOTTOM = (auto(), "midbottom")

    def type(self):
        return self.value[1]
