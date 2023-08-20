#!/usr/bin/env python3
import pygame
from pygame.locals import *
import sys
from speed import Speedometer
from gear import GearIndicator
from rpm import RPM
from granturismo.intake import Feed 
from unittest.mock import Mock


W = 800 
H = 480

if __name__ == "__main__":
  if len(sys.argv) < 2:
    print(f"\n*** Usage with PS5: {sys.argv[0]} <PS5-IP>")
    ip_address = None
  else:
    ip_address = sys.argv[1]

  pygame.init()
  screen = pygame.display.set_mode((W,H), pygame.FULLSCREEN)
  monitor_size = [pygame.display.Info().current_w, pygame.display.Info().current_h]

  sprites = pygame.sprite.Group()
  sprites.add(Speedometer(360, 160, (W-360)//2+160, (H-160)//2))
  sprites.add(GearIndicator(60,60, 720, 400))
  sprites.add(RPM(0,20))

  packet = Mock()
  packet.car_speed = 0/3.6
  packet.current_gear = None

  sprites.update(packet)
  sprites.draw(screen)
  pygame.display.flip()

  fullscreen = True

  if ip_address != None:
    listener = Feed(ip_address)
    listener.start()

  while True:
    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        if ip_address != None:
          listener.close()
        pygame.quit()
        sys.exit()
      if event.type == KEYDOWN:
        if event.key == K_ESCAPE:
          if ip_address != None:
            listener.close()
          pygame.quit()
          sys.exit()
        if event.key == K_f:
          fullscreen = not fullscreen
          if fullscreen:
            screen = pygame.display.set_mode(monitor_size, pygame.FULLSCREEN)
          else:
            screen = pygame.display.set_mode((W,H), pygame.RESIZABLE)

    if ip_address != None:
      packet = listener.get()
    sprites.update(packet)
    screen.fill((0,0,0))
    sprites.draw(screen)
    pygame.display.flip()

