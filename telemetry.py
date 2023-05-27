from granturismo import Feed
import sys
import curses


if __name__ == '__main__':

  ip_address = sys.argv[1]
  stdscr = curses.initscr()

  with Feed(ip_address) as feed:
    while True:
      packet = feed.get()

      stdscr.addstr(0, 0, f'{packet.car_speed * 3.6} km/h')
      stdscr.refresh()

  
