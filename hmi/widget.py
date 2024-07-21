import pygame
from hmi.color import Color


class AbstractWidget(pygame.sprite.Sprite):
    def __init__(self, w, h, x, y, primary_font_size=40, secondary_font_size=46):
        super().__init__()
        self.image = pygame.Surface((w, h)).convert()
        self.rect = self.image.get_rect(topleft=(x, y))
        self.primary_font = pygame.font.Font(
            "fonts/digital-7-mono.ttf", primary_font_size
        )
        self.recondary_font = pygame.font.Font(
            "fonts/pixeltype.ttf", secondary_font_size
        )

    def draw_overlay(self):
        pygame.draw.rect(self.image, Color.DARK_GREY.rgb(), self.image.get_rect(), 0, 8)
        pygame.draw.rect(self.image, Color.GREY.rgb(), self.image.get_rect(), 1, 8)

    def update(self, data):
        self.draw_overlay()
