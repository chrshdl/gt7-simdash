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
    from granturismo.intake import Listener
    listener = Listener(ip_address)
    listener.start()

  pygame.init()
  screen = pygame.display.set_mode((W,H), pygame.RESIZABLE)
  monitor_size = [pygame.display.Info().current_w, pygame.display.Info().current_h]
  clock = pygame.time.Clock()

  bg = pygame.image.load("rpm1.png")
 # bg.set_alpha(128)
  bg = pygame.transform.scale(bg, (.96*bg.get_rect().width, .96*bg.get_rect().height))

  sprites = pygame.sprite.Group()

  sprites.add(Speedometer(360, 160, (W-160)//2, (H+160)//2))
  sprites.add(GearIndicator(60,60, 720, 400))

  width = 10
  height = 270
  margin = 1
  offset = 2

  sprites.add(
    RPM(
      offset + (margin + width) * step + margin,
      0,
      width,
      height,
      step) for step in range(71)
  )


  screen.blit(bg, bg.get_rect())

  packet = Mock()
  packet.car_speed = 0/3.6
  packet.current_gear = None
  packet.engine_rpm = 0.0

  fullscreen = False

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
      packet.engine_rpm = (packet.engine_rpm + 10) % 7001
      packet.car_speed = (packet.car_speed + 1) % 255 
    sprites.update(packet)
    sprites.draw(screen)
    screen.blit(bg, bg.get_rect())
    pygame.display.flip()
    clock.tick(60)

