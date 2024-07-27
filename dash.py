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
        self._car_id = -1

        ps5_ip = conf["ps5_ip"]

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

        self.listener = Feed(ps5_ip)

    def run(self):

        self.running = True

        clock = pygame.time.Clock()
        hmi = HMI()
        led = LED()

        self.listener.start()
        self.logger.info("SENDING HEARTBEAT")
        self.listener.send_heartbeat()
        last_heartbeat = 0

        while self.running:

            dt = clock.tick() / 1000

            try:
                packet = self.listener.get()
            except Exception as e:
                self.logger.warning(f"CONNECTION ISSUE: {e}")
                self.logger.info("TRYING TO RECONNECT, SENDING HEARTBEAT")
                self.listener.send_heartbeat()
                last_heartbeat = 0
                continue

            if packet.received_time - last_heartbeat >= Dash.HEARTBEAT_DELAY:
                last_heartbeat = packet.received_time
                self.logger.info("SENDING HEARTBEAT")
                self.listener.send_heartbeat()

            events = pygame.event.get()

            for event in events:
                if event.type == Event.HMI_CAR_CHANGED.type():
                    hmi.update_rpm_alerts(packet.rpm_alert.min, packet.rpm_alert.max)

                if event.type == pygame.QUIT:
                    self.running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                    if event.key == pygame.K_SPACE:
                        screenshot = pygame.Surface((self.W, self.H))
                        screenshot.blit(pygame.display.get_surface(), (0, 0))
                        pygame.image.save(screenshot, "gt7-simdash.png")

            hmi.draw(dt, packet)
            led.draw(events)
            self.car_id(packet.car_id)
            pygame.display.flip()

        self.close()

    def close(self):
        self.listener.close()
        pygame.quit()
        sys.exit()

    def car_id(self, id):
        if self._car_id != id:
            self._car_id = id
            pygame.event.post(
                pygame.event.Event(Event.HMI_CAR_CHANGED.type(), message=self._car_id)
            )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="PS5 sim dash")
    parser.add_argument("--config", help="json with the config", default="config.json")
    args = parser.parse_args()

    with open(args.config, "r") as fid:
        config = json.load(fid)

    dash = Dash(config)
    dash.run()
