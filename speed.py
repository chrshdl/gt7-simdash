import pygame

class Speedometer(pygame.sprite.Sprite):
  def __init__(self, w, h, pos):
    super().__init__()
    self.image = pygame.Surface((w,h)).convert()
    #self.image.fill((5,5,5)) #17,30,38
    self.rect = self.image.get_rect(center = pos)
    self.font = pygame.font.Font("digital-7-mono.ttf", 120)

  def update(self, data):
    self.image.fill((5,5,5)) #17,30,38
    speed =  str(int(data.car_speed * 3.6))
    speed = speed.center(len(speed))
    text = self.font.render(f"{speed}", True, (0,200,0)) #64,84,60
    self.image.blit(text, text.get_rect(center = self.image.get_rect().center))

