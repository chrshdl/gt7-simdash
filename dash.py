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
      self.packet = Mock()
      self.packet.car_speed = 0/3.6
      self.packet.current_gear = 1 
      self.packet.engine_rpm = 900.0
      self.packet.rpm_alert.min = 6000
      self.packet.rpm_alert.max = 7500
      self.packet.flags.rev_limiter_alert_active = False
      self.packet.last_lap_time = 165256
      
      self.listener = Mock()
      self.listener.get = MagicMock(name='get')
      self.listener.get.return_value = self.packet
      self.listener.close = MagicMock(name='close')
    
    self.packet = self.listener.get()
    self.hmi = HMI(self.packet.rpm_alert.max)


  def close(self):
    self.listener.close()
    pygame.quit()
    sys.exit()


  def _get(self):
    self.packet.engine_rpm = (self.packet.engine_rpm+50) % self.packet.rpm_alert.max
    if self.packet.engine_rpm >= self.packet.rpm_alert.min:
      self.packet.flags.rev_limiter_alert_active = True
    else:
      self.packet.flags.rev_limiter_alert_active = False
      if self.packet.engine_rpm < 50:
        self.packet.current_gear = (self.packet.current_gear + 1) % 7
    self.packet.car_speed = (self.packet.car_speed+.1) % (260/3.6)
    return self.packet


  def run(self):
    from unittest.mock import Mock
    while True:
      for event in pygame.event.get():
        if event.type == pygame.QUIT:
          self.close()
        if event.type == KEYDOWN:
          if event.key == K_ESCAPE:
            self.close()
      if isinstance(self.packet, Mock):
        self.packet = self._get()
      else:  
        self.packet = self.listener.get()
      self.hmi.run(self.packet)
      pygame.display.flip()
      self.clock.tick(60)

