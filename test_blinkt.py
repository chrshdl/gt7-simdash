import blinkt
import time

RED = (255,0,0)
GREEN = (0,255,0) #(21,255,11)
BLUE = (0,0,255)

colors = list()

def init():
  colors.append(BLUE)  
  colors.append(GREEN)  
  colors.append(GREEN)  
  colors.append(RED)  
  blinkt.set_brightness(.05)
  clear_all()

def clear_all():
  blinkt.clear()
  blinkt.show()


if __name__ == "__main__":

  init()

  while True:
    for i in range(blinkt.NUM_PIXELS//2):
      blinkt.set_pixel(i, colors[i][0], colors[i][1], colors[i][2])
      blinkt.set_pixel(blinkt.NUM_PIXELS - 1 - i, colors[i][0], colors[i][1], colors[i][2])
      blinkt.show()
      time.sleep(.5)

    for _ in range(4):
      clear_all()
      for i in range(blinkt.NUM_PIXELS//2):
        blinkt.set_pixel(i, colors[i][0], colors[i][1], colors[i][2])
        blinkt.set_pixel(blinkt.NUM_PIXELS - 1 - i, colors[i][0], colors[i][1], colors[i][2])
      blinkt.show()
      time.sleep(.05)
    clear_all()  

