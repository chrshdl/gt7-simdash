import pygame

class RPM(pygame.sprite.Sprite):
  def __init__(self, x, y):
    super().__init__()
    self.image = pygame.image.load("rpm0.png")
    self.image = pygame.transform.scale(self.image, (self.image.get_width(), self.image.get_height()))
    self.rect = self.image.get_rect()
    self.rect.x = x
    self.rect.y = y

  def update(self, data):
    pass
