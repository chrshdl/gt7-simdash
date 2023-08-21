import pygame

class RPM(pygame.sprite.Sprite):
  def __init__(self, w, h):
    super().__init__()
    self.image = pygame.Surface((w,h), pygame.SRCALPHA)
    self.image = self.image.convert_alpha()
    self.rect = self.image.get_rect()
    self.height = h

  def update(self, data):
    width = 10
    margin = 1
    offset = 2

    self.image.fill((17,30,38))

    rpm = int(data.engine_rpm) // 100

    for step in range(rpm):
      color = (64,84,60)
      pygame.draw.rect(self.image,
        color,
        [
          offset + (margin + width) * step + margin,
          0,
          width,
          self.height
        ]
      )

