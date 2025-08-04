import curses
import time

from granturismo.intake.feed import Feed, Packet


def main(stdscr, ip_addr):
    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.timeout(0)
    stdscr.clear()

    with Feed(ip_addr) as listener:
        while True:
            stdscr.erase()
            try:
                packet: Packet = listener.get_nowait()
                speed = int(packet.car_speed * 3.6)
                stdscr.addstr(0, 0, f"Speed: {speed} km/h")
            except Exception:
                stdscr.addstr(0, 0, "Waiting for data...")

            stdscr.addstr(2, 0, "Press ESC to quit.")
            stdscr.refresh()

            key = stdscr.getch()
            if key == 27:
                break

            time.sleep(1 / 60.0)


if __name__ == "__main__":
    import sys

    ip_addr = sys.argv[1] if len(sys.argv) > 1 else "10.22.33.55"
    curses.wrapper(main, ip_addr)
