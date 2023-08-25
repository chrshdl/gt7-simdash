import pygame

class RPM(pygame.sprite.Sprite):
  def __init__(self, x, y, w, h, name, color=(0,0,0)):
    super().__init__()
    self.image = pygame.Surface((w,h), pygame.SRCALPHA)
    self.image.fill(color)
    self.rect = self.image.get_rect()
    self.rect.x = x
    self.rect.y = y
    self.name = name

  def update(self, data):
    rpm = int(data.engine_rpm) // 100

    if self.name <= rpm:
      if rpm >= 64 and self.name >=64:
        self.image.fill((255,0,0))
      else:
        self.image.fill((64,84,60))
    else:
      self.image.fill((0,0,0))

