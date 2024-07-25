from posixpath import join
import pygame
from hmi.color import Color


class Widget(pygame.sprite.Sprite):
    def __init__(self, groups, w, h, main_fsize=40, header_fsize=46):
        super().__init__(groups)

        self.image = pygame.Surface((w, h)).convert()
        self.rect = self.image.get_rect(topleft=(0, 0))
        self.main_font = pygame.font.Font(
            join("fonts", "digital-7-mono.ttf"), main_fsize
        )
        self.header_font = pygame.font.Font("fonts/pixeltype.ttf", header_fsize)

    def draw_overlay(self):
        pygame.draw.rect(self.image, Color.DARK_GREY.rgb(), self.image.get_rect(), 0, 8)
        pygame.draw.rect(self.image, Color.GREY.rgb(), self.image.get_rect(), 1, 8)

    def update(self):
        self.draw_overlay()
