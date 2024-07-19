import pygame
import time


class Lap(pygame.sprite.Sprite):
    def __init__(self, w, h, x, y):
        super().__init__()
        self.image = pygame.Surface((w, h)).convert()
        self.rect = self.image.get_rect(topleft=(x, y))
        self.font = pygame.font.Font("digital-7-mono.ttf", 40)
        self.font2 = pygame.font.Font("pixeltype.ttf", 46)  # 36

    def draw_overlay(self):
        pygame.draw.rect(self.image, "#050505", self.image.get_rect())
        pygame.draw.rect(self.image, "#404040", self.image.get_rect(), 1, 8)

    def update(self, data):
        self.draw_overlay()


class LastLap(Lap):
    def update(self, data):
        super().update(data)

        llt = data.last_lap_time

        if llt is None:
            llt_str = "--:--"
        else:
            llt_str = time.strftime(
                "%M:%S.{}".format(llt % 1000), time.gmtime(llt / 1000.0)
            )
        llt_render = self.font.render(llt_str, True, (0, 200, 0))
        res = tuple(map(sum, zip(self.image.get_rect().midbottom, (0, 0))))
        self.image.blit(llt_render, llt_render.get_rect(midbottom=res))
        label = self.font2.render("Last Lap", False, (200, 200, 200))
        midtop = tuple(map(sum, zip(self.image.get_rect().midtop, (0, 10))))
        self.image.blit(label, label.get_rect(midtop=midtop))


class BestLap(Lap):
    def update(self, data):
        super().update(data)

        blt = data.best_lap_time

        if blt is None:
            blt_str = "--:--"
        else:
            blt_str = time.strftime(
                "%M:%S.{}".format(blt % 1000), time.gmtime(blt / 1000.0)
            )
        blt_render = self.font.render(blt_str, True, (0, 200, 0))
        res = tuple(map(sum, zip(self.image.get_rect().midbottom, (0, 0))))
        self.image.blit(blt_render, blt_render.get_rect(midbottom=res))
        label = self.font2.render("Best Lap", False, (200, 200, 200))
        midtop = tuple(map(sum, zip(self.image.get_rect().midtop, (0, 10))))
        self.image.blit(label, label.get_rect(midtop=midtop))
