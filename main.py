import pygame
from pygame.locals import *
import sys
from speed import Speedometer
from granturismo.intake import Listener

W = 800 
H = 480

if __name__ == "__main__":
  if len(sys.argv) < 2:
    print(f"\n*** Usage: {sys.argv[0]} <ps5-IP>")
    exit(-1)

  ip_address = sys.argv[1]

  pygame.init()
  screen = pygame.display.set_mode((W,H), pygame.RESIZABLE)
  monitor_size = [pygame.display.Info().current_w, pygame.display.Info().current_h]

  sprites = pygame.sprite.Group()
  sprites.add(Speedometer(240, 130, (W-240)//2, (H-130)//2))
  
  fullscreen = False

  listener = Listener(ip_address)
  listener.start()

  try:
    while True:
      for event in pygame.event.get():
        if event.type == pygame.QUIT:
          pygame.quit()
          sys.exit()
        if event.type == KEYDOWN:
          if event.key == K_ESCAPE:
            pygame.quit()
            sys.exit()
          if event.key == K_f:
            fullscreen = not fullscreen
            if fullscreen:
              screen = pygame.display.set_mode(monitor_size, pygame.FULLSCREEN)
            else:
              screen = pygame.display.set_mode((W,H), pygame.RESIZABLE)

      packet = listener.get()
      sprites.update(int(3.6*packet.car_speed))
      sprites.draw(screen)
      pygame.display.update()

  finally:
    listener.close()

