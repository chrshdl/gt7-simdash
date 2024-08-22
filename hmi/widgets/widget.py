from os.path import join

import pygame

from hmi.properties import Color, TextAlignment


class Widget(pygame.sprite.Sprite):
    def __init__(self, groups, w, h, mfs=40, hfs=46):
        super().__init__(groups)

        self.header_text = None
        self.header_color = Color.WHITE.rgb()
        self.body_text = None
        self.body_text_color = Color.WHITE.rgb()
        self.body_text_alignment = TextAlignment.MIDBOTTOM

        self.image = pygame.Surface((w, h), pygame.SRCALPHA).convert_alpha()
        self.rect = self.image.get_rect(topleft=(0, 0))
        self.main_font = pygame.font.Font(join("fonts", "digital-7-mono.ttf"), mfs)
        self.header_font = pygame.font.Font(join("fonts", "pixeltype.ttf"), hfs)
        self.antialiased = False

    def draw_overlay(self, use_gradient, use_border):
        if use_gradient:
            self.draw_gradient(
                top=pygame.Color(0, 50, 124), bottom=pygame.Color(0, 3, 8)
            )
            pygame.draw.rect(self.image, Color.BLUE.rgb(), self.image.get_rect(), 2, 4)
        else:
            pygame.draw.rect(self.image, Color.BLACK.rgb(), self.image.get_rect(), 0, 4)
            if use_border:
                pygame.draw.rect(
                    self.image, Color.GREY.rgb(), self.image.get_rect(), 2, 4
                )

    def draw_gradient(self, top, bottom):
        w = self.image.get_rect().width
        h = self.image.get_rect().height
        for y in range(0, h, 5):
            color = top.lerp(bottom, y / h)
            self.image.fill(color, (0, y, w, 5))

    def draw_header(self):
        if self.header_text is not None:
            width = self.image.get_rect().width // 2 + 2
            label = self.header_font.render(
                self.header_text, self.antialiased, self.header_color
            )
            self.image.blit(label, label.get_rect(midtop=(width, 6)))

    def draw_body(self):
        if self.body_text is not None:
            result = self.main_font.render(
                f"{self.body_text}", self.antialiased, self.body_text_color
            )
            if self.body_text_alignment == TextAlignment.CENTER:
                self.image.blit(
                    result, result.get_rect(center=self.image.get_rect().center)
                )
            elif self.body_text_alignment == TextAlignment.MIDBOTTOM:
                self.image.blit(
                    result, result.get_rect(midbottom=self.image.get_rect().midbottom)
                )

    def update(self, use_gradient=False, use_border=True):
        self.draw_overlay(use_gradient, use_border)
        self.draw_header()
        self.draw_body()
