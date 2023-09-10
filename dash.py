import pygame
from pygame.locals import *
import sys
from hmi import HMI


class Dash:
  def __init__(self, conf):
    W = conf["width"]
    H = conf["height"]
    fullscreen = conf["fullscreen"]
    ip_address = conf["ps5_ip"]

    pygame.init()
    self.clock = pygame.time.Clock()
    
    monitor_size = (pygame.display.Info().current_w, pygame.display.Info().current_h)
    screen = pygame.display.set_mode((W,H), pygame.RESIZABLE)
    if fullscreen: screen = pygame.display.set_mode(monitor_size, pygame.FULLSCREEN)

    if ip_address is not None:
      from granturismo.intake import Feed
      self.listener = Feed(ip_address)
      self.listener.start()
    else:
      from unittest.mock import Mock, MagicMock
      packet = Mock()
      packet.car_speed = 0/3.6
      packet.current_gear = None 
      packet.engine_rpm = 900.0
      packet.rpm_alert.min = 6500
      packet.rpm_alert.max = 8000
      packet.flags.rev_limiter_alert_active = False
      
      self.listener = Mock()
      self.listener.get = MagicMock(name='get')
      self.listener.get.return_value = packet
      self.listener.close = MagicMock(name='close')

    packet = self.listener.get()
    self.hmi = HMI(packet.rpm_alert.min, packet.rpm_alert.max)


  def close(self):
    self.listener.close()
    pygame.quit()
    sys.exit()


  def run(self):
    while True:
      for event in pygame.event.get():
        if event.type == pygame.QUIT:
          self.close()
        if event.type == KEYDOWN:
          if event.key == K_ESCAPE:
            self.close()
      packet = self.listener.get()
      self.hmi.run(packet)
      pygame.display.flip()
      self.clock.tick(60)

