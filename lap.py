import pygame
import time
from color import Color


class AbstractLap(pygame.sprite.Sprite):
    def __init__(self, w, h, x, y, primary_font_size=40):
        super().__init__()
        self.image = pygame.Surface((w, h)).convert()
        self.rect = self.image.get_rect(topleft=(x, y))
        self.font = pygame.font.Font("digital-7-mono.ttf", primary_font_size)
        self.font2 = pygame.font.Font("pixeltype.ttf", 46)

    def draw_overlay(self):
        pygame.draw.rect(self.image, Color.DARK_GREY.rgb(), self.image.get_rect())
        pygame.draw.rect(self.image, Color.GREY.rgb(), self.image.get_rect(), 1, 8)

    def update(self, data):
        self.draw_overlay()


class LastLap(AbstractLap):
    def update(self, data):
        super().update(data)

        llt = data.last_lap_time

        if llt is None:
            llt_str = "--:--"
        else:
            llt_str = time.strftime(
                "%M:%S.{}".format(llt % 1000), time.gmtime(llt / 1000.0)
            )
        llt_render = self.font.render(llt_str, False, Color.GREEN.rgb())
        res = tuple(map(sum, zip(self.image.get_rect().midbottom, (0, 0))))
        self.image.blit(llt_render, llt_render.get_rect(midbottom=res))
        label = self.font2.render("Last Lap", False, Color.WHITE.rgb())
        midtop = tuple(map(sum, zip(self.image.get_rect().midtop, (0, 10))))
        self.image.blit(label, label.get_rect(midtop=midtop))


class BestLap(AbstractLap):
    def update(self, data):
        super().update(data)

        blt = data.best_lap_time

        if blt is None:
            blt_str = "--:--"
        else:
            blt_str = time.strftime(
                "%M:%S.{}".format(blt % 1000), time.gmtime(blt / 1000.0)
            )
        blt_render = self.font.render(blt_str, False, Color.GREEN.rgb())
        res = tuple(map(sum, zip(self.image.get_rect().midbottom, (0, 0))))
        self.image.blit(blt_render, blt_render.get_rect(midbottom=res))
        label = self.font2.render("Best Lap", False, Color.WHITE.rgb())
        midtop = tuple(map(sum, zip(self.image.get_rect().midtop, (0, 10))))
        self.image.blit(label, label.get_rect(midtop=midtop))


class Lap(AbstractLap):
    def update(self, data):
        super().update(data)

        current_lap = data.laps_in_race
        all_laps = data.lap_count

        blt_render = self.font.render(
            f"{current_lap} / {all_laps}", False, Color.GREEN.rgb()
        )
        res = tuple(map(sum, zip(self.image.get_rect().midbottom, (0, 0))))
        self.image.blit(blt_render, blt_render.get_rect(midbottom=res))
        label = self.font2.render("Lap", False, Color.WHITE.rgb())
        midtop = tuple(map(sum, zip(self.image.get_rect().midtop, (0, 10))))
        self.image.blit(label, label.get_rect(midtop=midtop))
