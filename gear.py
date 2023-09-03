import pygame

class GearIndicator(pygame.sprite.Sprite):
  def __init__(self, w, h, x, y):
    super().__init__()
    self.image = pygame.Surface((w,h))
    self.image = self.image.convert()
    self.image.fill((5,5,5)) #17,30,38
    self.rect = self.image.get_rect()
    self.rect.x = x
    self.rect.y = y
    self.font = pygame.font.Font("digital-7-mono.ttf", 280)

    self.text_show = True
    self.blink_count = 0
    self.blink_stop = 3

  def blink_update(self):
    if self.blink_count < self.blink_stop:
      self.blink_count += 1
      self.text_show = not self.text_show
    elif self.blink_count == self.blink_stop:
      self.blink_count += 1
    else:
      self.blink_count = 0

  def update(self, data):
    self.image.fill((5,5,5)) #17,30,38

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
      color = (250,50,50)
      self.blink_update()
    else:
      color = (255,255,255)
    if (self.text_show):
      text = self.font.render(f"{gear}", True, color) #165,165,165
      self.image.blit(text, text.get_rect(center = self.image.get_rect().center))

