import pygame
import blinkt


class RGB(pygame.sprite.Sprite):

  RED = (255,0,0)
  GREEN = (0,255,0) #(21,255,11)
  BLUE = (0,0,255)

  def __init__(self, w, h, x, y):
    super().__init__()
    self.image = pygame.Surface((w,h))
    self.image.fill((0,0,0))
    self.rect = self.image.get_rect()

    self.colors = list()

    self.colors.append(RGB.BLUE)  
    self.colors.append(RGB.GREEN)  
    self.colors.append(RGB.GREEN)  
    self.colors.append(RGB.RED)  

    blinkt.set_brightness(.05)

    self.count = 0

  def update(self, data):
    if data.flags.rev_limiter_alert_active:
      self.count += 1
      if self.count % 8 == 0:
        self.show_all_rgb(RGB.RED)
      if self.count % 16 == 0:
        self.clear_all_rgb()
    else:
      if data.engine_rpm < 100:
        self.clear_all_rgb()
      elif data.engine_rpm >= 4500:
        self.show_rgb(2)
      elif data.engine_rpm >= 5000:
        self.show_rgb(4)
      elif data.engine_rpm >= 5500:
        self.show_rgb(6)
      elif data.engine_rpm >= 6000:
        self.show_rgb(8)

  def clear_all_rgb(self):
    blinkt.clear()
    blinkt.show()
    self.count = 0

  def show_rgb(self, amount):
    for i in range(amount//2):
      blinkt.set_pixel(i, self.colors[i][0], self.colors[i][1], self.colors[i][2])
      blinkt.set_pixel(blinkt.NUM_PIXELS - 1 - i, self.colors[i][0], self.colors[i][1], self.colors[i][2])
    blinkt.show()

  def show_all_rgb(self, color):
    blinkt.set_all(color[0], color[1], color[2])
    blinkt.show()
