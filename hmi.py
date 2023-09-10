import pygame
from speed import Speedometer
from gear import GearIndicator
from rpm import RPM


class HMI:
  def __init__(self, rpm_alert_min, rpm_alert_max):

    self.screen = pygame.display.get_surface()

    width = self.screen.get_size()[0]
    self.sprites = pygame.sprite.Group()
    self.sprites.add(Speedometer(220, 120, (width//2, 400)))
    self.sprites.add(GearIndicator(180, 240, (width//2, 190)))

    rpm_min = int(rpm_alert_min) // 100
    rpm_max = int(rpm_alert_max) // 100

    margin = 1
    offset = 15
    width = (width
             - rpm_max * margin
             - offset) // rpm_max
    height = 25

    self.sprites.add(
      RPM(
        offset + (margin + width) * step + margin,
        20,
        width,
        height,
        step) for step in range(rpm_max + 1)
    )
    #TODO: move to RPM
    if self.platform_name() == 'aarch64':
      from rgb import RGB
      self.sprites.add(RGB(1,1,1,1))


  def platform_name(self):
    import platform
    return platform.uname()[4]


  def run(self, packet):
    self.sprites.update(packet)
    self.sprites.draw(self.screen)
