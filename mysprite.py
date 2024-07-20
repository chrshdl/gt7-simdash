import pygame


class AbstractSprite(pygame.sprite.Sprite):
    def __init__(self, w, h, x, y, fsize):
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

        dbg_car = f"car_id: {data.car_id}"
        dbg = self.font.render(dbg_car, True, (200, 200, 200))
        midtop = tuple(map(sum, zip(self.image.get_rect().midtop, (0, 10))))
        self.image.blit(dbg, dbg.get_rect(midtop=midtop))

        dbg_track = f"track: {flags.car_on_track}"
        dbg2 = self.font.render(dbg_track, True, (200, 200, 200))
        center = self.image.get_rect().center
        self.image.blit(dbg2, dbg2.get_rect(center=center))

        dbg_paused = f"paused: {flags.paused}"
        dbg3 = self.font.render(dbg_paused, True, (200, 200, 200))
        midbottom = tuple(map(sum, zip(self.image.get_rect().midbottom, (0, -10))))
        self.image.blit(dbg3, dbg3.get_rect(midbottom=midbottom))
