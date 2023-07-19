import pygame
from speed import Odometer

W = 800 
H = 480

pygame.init()
screen = pygame.display.set_mode((W,H))
clock = pygame.time.Clock()

middle_group = pygame.sprite.Group()
ow = 240
oh = 130
middle_group.add(Odometer(ow, oh, (W-ow)//2, (H-oh)//2))

active = True

while active:
  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      active = False
  
  middle_group.update()
  middle_group.draw(screen)
  pygame.display.update()

  clock.tick(30)

pygame.quit()  
 
