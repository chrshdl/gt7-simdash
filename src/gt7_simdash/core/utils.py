from enum import StrEnum
from importlib.resources import as_file, files

import pygame


def load_font(size: int, dir: str = None, name: str = None):
    p = f"assets/fonts/{dir}/{name}.ttf" if dir else f"assets/fonts/{name}.ttf"
    font_res = files("gt7_simdash").joinpath(p)
    with as_file(font_res) as font_path:
        return pygame.font.Font(str(font_path), size)


class FontFamily(StrEnum):
    DIGITAL_7_MONO = "digital-7-mono"
    PIXEL_TYPE = "pixeltype"
    NOTOSANS_REGULAR = "NotoSans-Regular"
    MATERIAL_SYMBOLS = "material-symbols-rounded-latin-300-normal"
    D_DIN = "D-DIN"
    D_DIN_BOLD = "D-DIN-Bold"
    D_DIN_EXP = "D-DINExp"
    D_DIN_EXP_BOLD = "D-DINExp-Bold"
    SILKSCREEN = "slkscr"
    SILKSCREEN_EXPANDED = "sslkscre"
