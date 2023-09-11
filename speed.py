import pygame

class Speedometer(pygame.sprite.Sprite):
  def __init__(self, w, h, pos):
    super().__init__()
    self.image = pygame.Surface((w,h)).convert()
    self.rect = self.image.get_rect(center=pos)
    self.font = pygame.font.Font("digital-7-mono.ttf", 110)
    self.font2 = pygame.font.Font("pixeltype.ttf", 36)


  def draw_overlay(self):
    pygame.draw.rect(self.image, '#050505', self.image.get_rect())
    pygame.draw.rect(self.image, '#404040', self.image.get_rect(), 1, 4)


  def update(self, data):
    self.draw_overlay()
    speed =  str(int(data.car_speed * 3.6))
    speed = speed.center(len(speed))
    speed = self.font.render(f"{speed}", True, (0,200,0))
    self.image.blit(speed, speed.get_rect(midbottom=self.image.get_rect().midbottom))
    label = self.font2.render("Speed", False, (200,200,200))
    self.image.blit(label, label.get_rect(midtop=self.image.get_rect().midtop))

