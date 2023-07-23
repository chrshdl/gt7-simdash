import pygame
from pygame.locals import *
import sys
from speed import Speedometer

W = 800 
H = 480

pygame.init()
screen = pygame.display.set_mode((W,H), pygame.RESIZABLE)
monitor_size = [pygame.display.Info().current_w, pygame.display.Info().current_h]
clock = pygame.time.Clock()

sprites = pygame.sprite.Group()
sprites.add(Speedometer(240, 130, (W-240)//2, (H-130)//2))

fullscreen = False

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
  
  sprites.update()
  sprites.draw(screen)
  pygame.display.update()

  clock.tick(60)

