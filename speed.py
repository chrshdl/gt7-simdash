import pygame

class Speedometer(pygame.sprite.Sprite):
  def __init__(self, w, h, x, y):
    super().__init__()
    self.image = pygame.Surface((w,h))
    self.image = self.image.convert()
    self.image.fill((5,5,5)) #17,30,38
    self.rect = self.image.get_rect()
    self.rect.x = x
    self.rect.y = y
    self.font = pygame.font.Font("digital-7-mono.ttf", 120)
    self.font2 = pygame.font.Font("digital-7-mono.ttf", 30)

  def update(self, data):
    self.image.fill((5,5,5)) #17,30,38
    speed =  str(int(data.car_speed * 3.6))
    speed = speed.center(len(speed))
    text = self.font.render(f"{speed}", True, (0,200,0)) #64,84,60
    self.image.blit(text, text.get_rect(center = self.image.get_rect().center))
    km_h = self.font2.render("KM/H", True, (255,255,255))
    #self.image.blit(km_h, km_h.get_rect(center = self.image.get_rect().center)) 

