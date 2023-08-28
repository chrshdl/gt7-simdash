import pygame

class GearIndicator(pygame.sprite.Sprite):
  def __init__(self, w, h, x, y):
    super().__init__()
    self.image = pygame.Surface((w,h))
    self.image.fill((17,30,38))
    self.rect = self.image.get_rect()
    self.rect.x = x
    self.rect.y = y
    self.font = pygame.font.Font("digital-7-mono.ttf", 320)

  def update(self, data):
    self.image.fill((0,0,0))
    if data.flags.in_gear == False:
      gear = "N"
    else:
      if data.current_gear == 0:
        gear = "R"
      elif data.current_gear == None:
        gear = "N"
      else:
        gear = str(data.current_gear)

    text = self.font.render(f"{gear}", True, (165,165,165))
    self.image.blit(text, [60,-30])

