import pygame
from speed import Speedometer
from gear import GearIndicator
from rpm import RPM
from lap import LastLap


class HMI:
  def __init__(self, rpm_max):
    self.screen = pygame.display.get_surface()
    self.sprites = pygame.sprite.Group()
    self.sprites.add(Speedometer(180, 120))
    self.sprites.add(GearIndicator(180, 220))
    self.sprites.add(LastLap(180, 80))

    rpm_max = int(rpm_max) // 100

    self.rpm = pygame.sprite.Group()
    self.add_rpm(140, rpm_max)


  def add_rpm(self, y, rpm_max):
    screen_width = self.screen.get_size()[0]
    self.rpm.add(
      RPM(screen_width, y, rpm_max, step) for step in range(rpm_max + 1)
    )
    # FIXME: DISPLAY GLITCHES ON RASPBERRY PI /W HYPERPIXEL
    #import platform  # TODO: move to class RPM?
    #if platform.machine().lower() == 'aarch64':
    #  from rgb import RGB
    #  self.rpm.add(RGB(1,1,1,1))



  def empty_rpm(self):
    self.rpm.empty()


  def update_rpm(self, packet):
    self.rpm.update(packet)
    self.rpm.draw(self.screen)


  def update_sprites(self, packet):
    self.sprites.update(packet)
    self.sprites.draw(self.screen)


  def run(self, packet):
    self.update_sprites(packet)
    self.update_rpm(packet)
