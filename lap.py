import pygame
import time


class LastLap(pygame.sprite.Sprite):
  def __init__(self, w, h):
    super().__init__()
    screen = pygame.display.get_surface()
    self.image = pygame.Surface((w,h)).convert()
    self.rect = self.image.get_rect(topleft=(610,160))  # (screen.get_size()[0]//2, 400)
    self.font = pygame.font.Font("digital-7-mono.ttf", 40)
    self.font2 = pygame.font.Font("pixeltype.ttf", 36)


  def draw_overlay(self):
    pygame.draw.rect(self.image, '#050505', self.image.get_rect())
    pygame.draw.rect(self.image, '#404040', self.image.get_rect(), 1, 8)


  def update(self, data):
    self.draw_overlay()
    if data.last_lap_time is None:
      llt = "--:--"
    else:
      time_ms = data.last_lap_time
      llt = time.strftime('%M:%S.{}'.format(time_ms%1000), time.gmtime(time_ms/1000.0))
    llt = self.font.render(llt, True, (0,200,0))
    res = tuple(map(sum, zip(self.image.get_rect().midbottom, (0,0))))
    self.image.blit(llt, llt.get_rect(midbottom=res))
    label = self.font2.render("Last Lap", False, (200,200,200))
    midtop = tuple(map(sum, zip(self.image.get_rect().midtop, (0,10))))
    self.image.blit(label, label.get_rect(midtop=midtop))
