import pygame

class RPM(pygame.sprite.Sprite):
  def __init__(self, x, y, w, h, name, color=(0,0,0)):
    super().__init__()
    self.image.fill(color)
    self.rect = self.image.get_rect()
    self.rect.x = x
    self.rect.y = y
    self.name = name
    if self.name % 10 == 0:
      self.image = pygame.Surface((w,h+10))
    else:
      self.image = pygame.Surface((w,h))
      

  def update(self, data):
    rpm = int(data.engine_rpm) // 100
    rpm_alert = int(data.rpm_alert.min) // 100

    if self.name <= rpm:
      if rpm >= rpm_alert and self.name >= rpm_alert:
        self.image.fill((82,24,21))
      else:
        self.image.fill((5,44,27))
    else:
      if self.name % 10 == 0:
        self.image.fill((30,30,30))
      else:
        self.image.fill((0,0,0))

