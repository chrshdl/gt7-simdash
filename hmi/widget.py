import pygame
from posixpath import join
from hmi.properties import Color, Alignment


class Widget(pygame.sprite.Sprite):
    def __init__(self, groups, w, h, main_fsize=40, header_fsize=46):
        super().__init__(groups)

        self.header_text = None
        self.header_color = Color.WHITE.rgb()
        self.body_text = None
        self.body_color = Color.GREEN.rgb()
        self.body_alignment = Alignment.MIDBOTTOM

        self.image = pygame.Surface((w, h)).convert()
        self.rect = self.image.get_rect(topleft=(0, 0))
        self.main_font = pygame.font.Font(
            join("fonts", "digital-7-mono.ttf"), main_fsize
        )
        self.header_font = pygame.font.Font(
            join("fonts", "pixeltype.ttf"), header_fsize
        )
        self.antialiased = False

    def draw_overlay(self):
        pygame.draw.rect(self.image, Color.DARK_GREY.rgb(), self.image.get_rect(), 0, 8)
        pygame.draw.rect(self.image, Color.GREY.rgb(), self.image.get_rect(), 1, 8)

    def draw_header(self):
        if self.header_text is not None:
            width = self.image.get_rect().width // 2 + 2
            label = self.header_font.render(
                self.header_text, self.antialiased, self.header_color
            )
            self.image.blit(label, label.get_rect(midtop=(width, 8)))

    def draw_body(self):
        if self.body_text is not None:
            result = self.main_font.render(
                f"{self.body_text}", self.antialiased, self.body_color
            )
            if self.body_alignment == Alignment.CENTER:
                self.image.blit(
                    result, result.get_rect(center=self.image.get_rect().center)
                )
            elif self.body_alignment == Alignment.MIDBOTTOM:
                self.image.blit(
                    result, result.get_rect(midbottom=self.image.get_rect().midbottom)
                )

    def update(self):
        self.draw_overlay()
        self.draw_header()
        self.draw_body()
