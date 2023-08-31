import pygame

class Speedometer(pygame.sprite.Sprite):
  def __init__(self, w, h, x, y):
    super().__init__() 
    self.image = pygame.Surface((w,h))
    #self.image.fill((17,30,38))
    self.image.fill((0,0,0))
    self.rect = self.image.get_rect() 
    self.rect.x = x
    self.rect.y = y
    self.font = pygame.font.Font("digital-7-mono.ttf", 200)
    self.font2 = pygame.font.Font("digital-7-mono.ttf", 30)

  def update(self, data):
    #self.image.fill((17,30,38))
    self.image.fill((0,0,0))
    speed =  int(data.car_speed * 3.6)
    text = self.font.render(f"{str(speed):>3}", True, (64,84,60))
    self.image.blit(text, (10,-17))
    km_h = self.font2.render("KM/H", True, (255,255,255))
    self.image.blit(km_h, (300,120))

