#!/usr/bin/env python3
import argparse
import json
import pygame
from pygame.locals import *
import sys
from speed import Speedometer
from gear import GearIndicator
from rpm import RPM
from unittest.mock import Mock


def run(conf):

  W = conf["width"] 
  H = conf["height"]
  fullscreen = conf["fullscreen"]
  ip_address = conf["ps5_ip"]

  if ip_address != None:
    from granturismo.intake import Feed
    listener = Feed(ip_address)
    listener.start()
  else:
    packet = Mock()
    packet.car_speed = 0/3.6
    packet.current_gear = 3
    packet.engine_rpm = 0.0
    packet.rpm_alert.min = 4500

  pygame.init()

  if fullscreen:
    screen = pygame.display.set_mode((W,H), pygame.FULLSCREEN)
  else:
    screen = pygame.display.set_mode((W,H), pygame.RESIZABLE)

  monitor_size = [pygame.display.Info().current_w, pygame.display.Info().current_h]
  clock = pygame.time.Clock()

  sprites = pygame.sprite.Group()

  sprites.add(Speedometer(360, 160, 0, 200))
  sprites.add(GearIndicator(260,260, 520, 120))

  packet = listener.get()
  rpm_max = int(packet.rpm_alert.max) // 100
  print(f"rpm max={rpm_max}")

  width = W//rpm_max
  height = 70
  margin = 1
  offset = 2

  sprites.add(
    RPM(
      offset + (margin + width) * step + margin,
      20,
      width,
      height,
      step) for step in range(rpm_max + 1)
  )


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
      packet.engine_rpm = (packet.engine_rpm + 30) % 7001
      packet.car_speed = (packet.car_speed + 1) % 255

    sprites.update(packet)
    sprites.draw(screen)
    pygame.display.flip()
    clock.tick(60)


if __name__ == "__main__":
  parser = argparse.ArgumentParser(description="PS5 sim dash")
  parser.add_argument("--config", help="json with the config", default="config.json")
  args = parser.parse_args()

  with open(args.config, 'r') as fid:
    config = json.load(fid)

  run(config)


