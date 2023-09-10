import pygame
import time


class GearIndicator(pygame.sprite.Sprite):
  def __init__(self, w, h, pos):
    super().__init__()
    self.image = pygame.Surface((w,h)).convert()
    #self.image.fill((5,5,5)) #17,30,38
    #pygame.draw.rect(self.image, 'gray', self.image.get_rect(), 1, 20)
    self.rect = self.image.get_rect(center = pos)
    self.font = pygame.font.Font("digital-7-mono.ttf", 280)
    self.text_show = True
    self.blink_count = 0
    self.blink_stop = 1
    self.start_time = 0

  def reset_ticks(self):
    self.start_time = pygame.time.get_ticks()  

  def blink_update(self):
    print(pygame.time.get_ticks() - self.start_time)
    if self.blink_count < self.blink_stop:
      self.blink_count += 1
      self.text_show = not self.text_show
    elif self.blink_count == self.blink_stop:
      self.blink_count += 1
    else:
      self.blink_count = 0

  def update(self, data):
    self.image.fill((5,5,5)) #17,30,38
    #pygame.draw.rect(self.image, 'gray', self.image.get_rect(), 1, 20)
    
    if not data.flags.in_gear:
      gear = "N"
    else:
      if data.current_gear == 0:
        gear = "R"
      elif data.current_gear == None:
        gear = "N"
      else:
        gear = str(data.current_gear)

    if data.flags.rev_limiter_alert_active:
      color = (250,50,50)
      self.blink_update()
    else:
      color = (255,255,255)
      self.reset_ticks()
    if (self.text_show):
      text = self.font.render(f"{gear}", True, color) #165,165,165
      self.image.blit(text, text.get_rect(center = self.image.get_rect().center))

