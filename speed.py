import pygame
from color import Color


class Speedometer(pygame.sprite.Sprite):
    def __init__(self, w, h, x, y):
        super().__init__()
        self.image = pygame.Surface((w, h)).convert()
        self.rect = self.image.get_rect(topleft=(x, y))
        self.font = pygame.font.Font("digital-7-mono.ttf", 108)
        self.font2 = pygame.font.Font("pixeltype.ttf", 46)

    def draw_overlay(self):
        pygame.draw.rect(self.image, "#050505", self.image.get_rect())
        pygame.draw.rect(self.image, "#404040", self.image.get_rect(), 1, 8)

    def update(self, data):
        self.draw_overlay()
        speed = str(int(data.car_speed * 3.6))
        speed = speed.center(len(speed))
        speed = self.font.render(f"{speed}", False, Color.GREEN.rgb())
        res = tuple(map(sum, zip(self.image.get_rect().midbottom, (0, 4))))
        self.image.blit(speed, speed.get_rect(midbottom=res))
        label = self.font2.render("Speed", False, Color.WHITE.rgb())
        midtop = tuple(map(sum, zip(self.image.get_rect().midtop, (0, 10))))
        self.image.blit(label, label.get_rect(midtop=midtop))
