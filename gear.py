import pygame
from color import Color


class GearIndicator(pygame.sprite.Sprite):
    def __init__(self, w, h, x, y):
        super().__init__()
        self.image = pygame.Surface((w, h)).convert()
        self.rect = self.image.get_rect(center=(x, y))
        self.font = pygame.font.Font("digital-7-mono.ttf", 240)

    def draw_overlay(self):
        pygame.draw.rect(self.image, "#050505", self.image.get_rect())
        pygame.draw.rect(self.image, "#404040", self.image.get_rect(), 1, 4)

    def draw_gear(self, data):
        if not data.flags.in_gear:
            gear = "N"
        else:
            if data.current_gear == 0:
                gear = "R"
            elif data.current_gear == None:
                gear = "N"
            else:
                gear = str(data.current_gear)
        if data.flags.rev_limiter_alert_active:
            color = (250, 50, 50)
        else:
            color = Color.WHITE.rgb()
        gear_render = self.font.render(f"{gear}", False, color)
        self.image.blit(
            gear_render, gear_render.get_rect(center=self.image.get_rect().center)
        )

    def update(self, data):
        self.draw_overlay()
        self.draw_gear(data)
