import sys
import pygame
from hmi.view import View
from hmi.popup import Popup

from common.logger import Logger

from common.event import Event
from common.evendispatcher import EventDispatcher
from events import HMI_CAR_CHANGED, HMI_CONNECTION_ESTABLISHED

HEARTBEAT_DELAY = 10


class Dash:

    HEARTBEAT_DELAY = 10

    def __init__(self, conf):
        w = conf["width"]
        h = conf["height"]
        fullscreen = conf["fullscreen"]
        playstation_ip = conf["playstation_ip"]

        self.listener = None
        self.running = False
        self.last_heartbeat = 0
        self._car_id = -1

        pygame.init()

        monitor_size = (
            pygame.display.Info().current_w,
            pygame.display.Info().current_h,
        )
        if not fullscreen:
            pygame.display.set_mode((w, h), pygame.RESIZABLE)
        else:
            pygame.display.set_mode(monitor_size, pygame.FULLSCREEN)

        self.states = {"SPLASH": Popup(playstation_ip), "DASH": View()}
        self.state = next(iter(self.states))

        self.logger = Logger(self.__class__.__name__).get()

        EventDispatcher()

        EventDispatcher.add_listener(
            HMI_CONNECTION_ESTABLISHED, self.on_connection_established
        )

    def run(self):
        self.running = True
        clock = pygame.time.Clock()
        packet = None

        while self.running:

            clock.tick()

            if self.listener is not None:
                try:
                    packet = self.listener.get()
                except Exception as e:
                    self.logger.info(f"💀 CONNECTION ISSUE: {e}")
                    self.state = "SPLASH"

                if packet.received_time - self.last_heartbeat >= HEARTBEAT_DELAY:
                    self.last_heartbeat = packet.received_time
                    self.logger.info(f"💗")
                    self.listener.send_heartbeat()

            events = pygame.event.get()

            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False

            self.states[self.state].update(packet)
            self.car_id(packet)
            pygame.display.update()

        self.close()

    def close(self):
        self.listener.close()
        pygame.quit()
        sys.exit()

    def car_id(self, packet):
        if packet is not None:
            if self._car_id != packet.car_id:
                self._car_id = packet.car_id
                data = (packet.rpm_alert.min, packet.rpm_alert.max)
                EventDispatcher.dispatch(Event(HMI_CAR_CHANGED, data))

    def on_connection_established(self, event):
        self.state = "DASH"
        self.listener = event.data


if __name__ == "__main__":
    import argparse
    import json

    parser = argparse.ArgumentParser(description="Gran Turismo 7 simdash")
    parser.add_argument("--config", help="the config file", default="config.json")
    args = parser.parse_args()

    with open(args.config, "r") as fid:
        config = json.load(fid)

    Dash(config).run()
