import pygame

class Odometer(pygame.sprite.Sprite):
  def __init__(self, w, h, x, y):
    super().__init__() 
    self.speed = 0
    self.image = pygame.Surface((w,h))
    self.image.fill((17,30,38))
    self.rect = self.image.get_rect() 
    self.rect.x = x
    self.rect.y = y
    self.font = pygame.font.Font('digital-7-mono.ttf', 160)

  def update(self):
    self.image.fill((17,30,38))
    self.speed = (self.speed + 1) % 400
    self.text = self.font.render(f"{str(self.speed):>3}", True, (64,84,60))
    text_rect = self.text.get_rect()
    self.image.blit(self.text, [10,-17])
