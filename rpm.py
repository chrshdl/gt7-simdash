import pygame

GREEN = (40,90,27,20)
BLACK = (0,0,0,255)
RED = (250,0,0,255)
DARK_RED = (160,0,0,255)
GREY = (20,20,20,255)
DARK_GREY = (10,10,10,255)
BLUE = (0,0,255,255)

class RPM(pygame.sprite.Sprite):
  def __init__(self, x, y, w, h, name, color=BLACK):
    super().__init__()
    self.name = name
    if self.name % 10 == 0:
      self.image = pygame.Surface((w,h+5), pygame.SRCALPHA)
    else:
      self.image = pygame.Surface((w,h), pygame.SRCALPHA)
    self.image = self.image.convert_alpha()
    self.rect = self.image.get_rect()
    self.rect.x = x
    self.rect.y = y

  def update(self, data):
    rpm = int(data.engine_rpm) // 100
    rpm_alert_min = int(data.rpm_alert.min) // 100

    if self.name <= rpm:
      if rpm >= rpm_alert_min and self.name >= rpm_alert_min:
        self.image.fill(RED)
      else:
        self.image.fill(GREEN)
    else:
      #if self.name % 10 == 0 and self.name >= rpm_alert_min:
      if self.name >= rpm_alert_min:
        self.image.fill(DARK_RED)
      elif self.name % 10 == 0 and not self.name >= rpm_alert_min:
        self.image.fill(GREY)
      else:
        self.image.fill(DARK_GREY)
