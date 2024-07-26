import pygame
import sys
from hmi.hmi import HMI
from hmi.event import Event
from hmi.led import LED
import argparse
import json
import time
import logging
from logformatter import LogFormatter
from granturismo.intake import Feed


class Dash:

    HEARTBEAT_DELAY = 10

    def __init__(self, conf):
        self.W = conf["width"]
        self.H = conf["height"]
        fullscreen = conf["fullscreen"]

        self.running = False

        ps5_ip = conf["ps5_ip"]
        self.listener = Feed(ps5_ip)

        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging.DEBUG)

        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        ch.setFormatter(LogFormatter())
        self.logger.addHandler(ch)

        pygame.init()

        monitor_size = (
            pygame.display.Info().current_w,
            pygame.display.Info().current_h,
        )
        if not fullscreen:
            pygame.display.set_mode((self.W, self.H), pygame.RESIZABLE)
        else:
            pygame.display.set_mode(monitor_size, pygame.FULLSCREEN)

    def run(self):

        self.running = True

        clock = pygame.time.Clock()
        hmi = HMI()
        led = LED()

        self.listener.start()

        self.logger.info("SENDING HEARTBEAT")
        self.listener.send_heartbeat()
        last_heartbeat = time.time()

        while self.running:

            dt = clock.tick() / 1000

            events = pygame.event.get()

            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                    if event.key == pygame.K_SPACE:
                        screenshot = pygame.Surface((self.W, self.H))
                        screenshot.blit(pygame.display.get_surface(), (0, 0))
                        pygame.image.save(screenshot, "gt7-simdash.png")

            packet = self.listener.get()

            if packet.received_time - last_heartbeat >= Dash.HEARTBEAT_DELAY:
                last_heartbeat = packet.received_time
                self.logger.info("SENDING HEARTBEAT")
                self.listener.send_heartbeat()

            hmi.draw(dt, packet)
            led.draw(events)
            pygame.display.flip()

        self.close()

    def close(self):
        self.listener.close()
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="PS5 sim dash")
    parser.add_argument("--config", help="json with the config", default="config.json")
    args = parser.parse_args()

    with open(args.config, "r") as fid:
        config = json.load(fid)

    dash = Dash(config)
    dash.run()
