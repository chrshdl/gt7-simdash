from enum import StrEnum
from importlib.resources import as_file, files

import pygame


def load_font(size: int, name):
    font_res = files("gt7_simdash").joinpath(f"assets/fonts/{name}.ttf")
    with as_file(font_res) as font_path:
        return pygame.font.Font(str(font_path), size)


class FontFamily(StrEnum):
    DIGITAL_7_MONO = "digital-7-mono"
    PIXEL_TYPE = "pixeltype"
