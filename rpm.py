import pygame

GREEN = (40,90,27)
BLACK = (0,0,0)
RED = (250,0,0)
DARK_RED = (90,0,0)
GREY = (20,20,20)
DARK_GREY = (10,10,10)
BLUE = (0,0,255)


class RPM(pygame.sprite.Sprite):
  def __init__(self, screen_width, y, rpm_max, step):
    super().__init__()
    margin = 1
    w = 3
    h = 22
    offset_center = (screen_width - rpm_max * (margin + w)) // 2
    pos = ((offset_center + (margin + w) * step + margin), y)
    self.step = step
    if self.step % 10 == 0:
      self.image = pygame.Surface((w,h+5))
    else:
      self.image = pygame.Surface((w,h))
    self.image = self.image.convert()
    self.rect = self.image.get_rect(topleft=pos)


  def update(self, data):
    current_rpm = int(data.engine_rpm) // 100
    rpm_alert_min = int(data.rpm_alert.min) // 100

    if self.step <= current_rpm:
      if current_rpm >= rpm_alert_min and self.step >= rpm_alert_min:
        self.image.fill(RED)
      else:
        self.image.fill(GREEN)
    else:
      if self.step >= rpm_alert_min:
        self.image.fill(DARK_RED)
      elif self.step % 10 == 0 and not self.step >= rpm_alert_min:
        self.image.fill(GREY)
      else:
        self.image.fill(DARK_GREY)
