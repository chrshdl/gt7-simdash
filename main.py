#!/usr/bin/env python3
import argparse
import json
import pygame
from pygame.locals import *
import sys
from speed import Speedometer
from gear import GearIndicator
from rpm import RPM


def get_platform_name():
  import platform
  return platform.uname()[4]

def create_dash(W, rpm_alert_min, rpm_alert_max):
  sprites = pygame.sprite.Group()
  sprites.add(Speedometer(220, 120, (W-220)//2, 330))
  sprites.add(GearIndicator(160,220, (W-160)//2, 80))

  rpm_min = int(rpm_alert_min) // 100
  rpm_max = int(rpm_alert_max) // 100

  margin = 1
  offset = 15
  width = (W - (rpm_max * margin) - offset) // rpm_max
  height = 25

  sprites.add(
    RPM(
      offset + (margin + width) * step + margin,
      20,
      width,
      height,
      step) for step in range(rpm_max + 1)
  )

  if get_platform_name() == 'aarch64':
    from rgb import RGB
    sprites.add(RGB(1,1,1,1))
  return sprites


def run(conf):
  W = conf["width"]
  H = conf["height"]
  fullscreen = conf["fullscreen"]
  ip_address = conf["ps5_ip"]


  if ip_address is not None:
    from granturismo.intake import Feed
    listener = Feed(ip_address)
    listener.start()
    packet = listener.get()
  else:
    from unittest.mock import Mock
    packet = Mock()
    packet.car_speed = 0/3.6
    packet.current_gear = 1 
    packet.engine_rpm = 0.0
    packet.rpm_alert.min = 6500
    packet.rpm_alert.max = 8000
    packet.flags.rev_limiter_alert_active = False

  pygame.init()
  clock = pygame.time.Clock()
  monitor_size = (pygame.display.Info().current_w, pygame.display.Info().current_h)

  if fullscreen:
    screen = pygame.display.set_mode(monitor_size, pygame.FULLSCREEN)
  else:
    screen = pygame.display.set_mode((W,H), pygame.RESIZABLE)

  dash = create_dash(W, packet.rpm_alert.min, packet.rpm_alert.max)


  while True:
    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        if ip_address is not None:
          listener.close()
        pygame.quit()
        sys.exit()
      if event.type == KEYDOWN:
        if event.key == K_ESCAPE:
          if ip_address is not None:
            listener.close()
          pygame.quit()
          sys.exit()
        if event.key == K_f:
          fullscreen = not fullscreen
          if fullscreen:
            screen = pygame.display.set_mode(monitor_size, pygame.FULLSCREEN)
          else:
            screen = pygame.display.set_mode((W,H), pygame.RESIZABLE)

    if ip_address is not None:
      packet = listener.get()
    else:
      packet.engine_rpm = (packet.engine_rpm + 50) % packet.rpm_alert.max
      if packet.engine_rpm >= packet.rpm_alert.min:
        packet.flags.rev_limiter_alert_active = True
      else:
        packet.flags.rev_limiter_alert_active = False
        if packet.engine_rpm < 50:
          packet.current_gear = (packet.current_gear + 1) % 6
      packet.car_speed = (packet.car_speed + .1) % (255/3.6)

    dash.update(packet)
    dash.draw(screen)
    pygame.display.flip()
    clock.tick(60)


if __name__ == "__main__":
  parser = argparse.ArgumentParser(description="PS5 sim dash")
  parser.add_argument("--config", help="json with the config", default="config.json")
  args = parser.parse_args()

  with open(args.config, 'r') as fid:
    config = json.load(fid)

  run(config)

