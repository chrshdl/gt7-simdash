import pygame
from color import Color


class AbstractSprite(pygame.sprite.Sprite):
    def __init__(self, w, h, x, y, fsize=32):
        super().__init__()
        self.image = pygame.Surface((w, h)).convert()
        self.rect = self.image.get_rect(topleft=(x, y))
        self.font = pygame.font.Font("pixeltype.ttf", fsize)

    def draw_overlay(self):
        pygame.draw.rect(self.image, "#050505", self.image.get_rect())
        pygame.draw.rect(self.image, "#404040", self.image.get_rect(), 1, 8)

    def update(self, data):
        self.draw_overlay()


class DebugSprite(AbstractSprite):
    def update(self, data):
        super().update(data)

        flags = data.flags

        dbg_track = f"on track: {flags.car_on_track}"
        dbg = self.font.render(dbg_track, False, Color.LIGHT_GREY.rgb())
        midtop = tuple(map(sum, zip(self.image.get_rect().midtop, (0, 10))))
        self.image.blit(dbg, dbg.get_rect(midtop=midtop))

        dbg_loading = f"loading: {flags.loading_or_processing}"
        dbg2 = self.font.render(dbg_loading, False, Color.LIGHT_GREY.rgb())
        center = self.image.get_rect().center
        self.image.blit(dbg2, dbg2.get_rect(center=center))

        dbg_paused = f"paused: {flags.paused}"
        dbg3 = self.font.render(dbg_paused, False, Color.LIGHT_GREY.rgb())
        midbottom = tuple(map(sum, zip(self.image.get_rect().midbottom, (0, -10))))
        self.image.blit(dbg3, dbg3.get_rect(midbottom=midbottom))


class InitializingSprite(AbstractSprite):
    def update(self, data):
        self.font = pygame.font.Font("pixeltype.ttf", 56)
        data_render = self.font.render(data, True, (200, 200, 200))
        center = self.image.get_rect().center
        self.image.blit(data_render, data_render.get_rect(center=center))
