import pygame

class GearIndicator(pygame.sprite.Sprite):
  def __init__(self, w, h, x, y):
    super().__init__()
    self.image = pygame.Surface((w,h))
    self.image = self.image.convert()
    self.image.fill((17,30,38))
    self.rect = self.image.get_rect()
    self.rect.x = x
    self.rect.y = y
    self.font = pygame.font.Font("digital-7-mono.ttf", 280)

  def update(self, data):
    self.image.fill((17,30,38))

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
      color = (255,0,0)
    else:
      color = (255,255,255)
    text = self.font.render(f"{gear}", True, color) #165,165,165
    self.image.blit(text, text.get_rect(center = self.image.get_rect().center))

