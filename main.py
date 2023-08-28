#!/usr/bin/env python3
import pygame
from pygame.locals import *
import sys
from speed import Speedometer
from gear import GearIndicator
from rpm import RPM
from unittest.mock import Mock


W = 800 
H = 480

if __name__ == "__main__":
  if len(sys.argv) < 2:
    print(f"\n*** Usage with PS5: {sys.argv[0]} <PS5-IP>")
    ip_address = None
  else:
    ip_address = sys.argv[1]
    from granturismo.intake import Feed
    listener = Feed(ip_address)
    listener.start()

  pygame.init()
  screen = pygame.display.set_mode((W,H), pygame.FULLSCREEN)
  monitor_size = [pygame.display.Info().current_w, pygame.display.Info().current_h]
  clock = pygame.time.Clock()

  sprites = pygame.sprite.Group()

  sprites.add(Speedometer(360, 160, 0, 200))
  sprites.add(GearIndicator(260,260, 520, 120))

  width = 10
  height = 70
  margin = 1
  offset = 2

  sprites.add(
    RPM(
      offset + (margin + width) * step + margin,
      20,
      width,
      height,
      step) for step in range(71)
  )

  packet = Mock()
  packet.car_speed = 0/3.6
  packet.current_gear = 3
  packet.engine_rpm = 0.0
  packet.rpm_alert.min = 4500

  fullscreen = True

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
    else:
      packet.engine_rpm = 4601 #(packet.engine_rpm + 30) % 7001
      packet.car_speed = 120/3.6 #(packet.car_speed + 1) % 255
    sprites.update(packet)
    sprites.draw(screen)
    # screen.blit(bg, bg.get_rect())
    pygame.display.flip()
    clock.tick(60)

