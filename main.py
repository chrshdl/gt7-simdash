import sys
import pygame
from hmi.view import View
from system.event import Event
from system.logger import Logger
from system.eventdispatcher import EventDispatcher
from granturismo.intake import Feed
from events import HMI_CAR_CHANGED


class Dash:

    HEARTBEAT_DELAY = 10

    def __init__(self, conf):
        w = conf["width"]
        h = conf["height"]
        fullscreen = conf["fullscreen"]
        ps_ip = conf["playstation_ip"]

        self.running = False
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

        self.listener = Feed(ps_ip)
        self.logger = Logger(self.__class__.__name__).get()
        EventDispatcher()

    def run(self):
        self.running = True
        clock = pygame.time.Clock()

        dash = View()

        last_heartbeat = self.send_handshake()

        while self.running:

            clock.tick()

            try:
                packet = self.listener.get()
            except Exception as e:
                self.logger.info(f"💀 CONNECTION ISSUE: {e}")
                last_heartbeat = self.send_handshake()
                continue

            if packet.received_time - last_heartbeat >= Dash.HEARTBEAT_DELAY:
                last_heartbeat = packet.received_time
                self.logger.info(f"💗")
                self.listener.send_heartbeat()

            events = pygame.event.get()

            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False

            dash.update(packet)
            self.car_id(packet)
            pygame.display.update()

        self.close()

    def send_handshake(self):
        if not self.listener._sock_bounded:
            self.listener.start()
        self.logger.info("🤝 SENDING HANDSHAKE...")
        self.listener.send_heartbeat()
        return 0

    def close(self):
        self.listener.close()
        pygame.quit()
        sys.exit()

    def car_id(self, packet):
        if self._car_id != packet.car_id:
            self._car_id = packet.car_id
            data = (packet.rpm_alert.min, packet.rpm_alert.max)
            EventDispatcher.dispatch(Event(HMI_CAR_CHANGED, data))


if __name__ == "__main__":
    import argparse
    import json

    parser = argparse.ArgumentParser(description="Gran Turismo 7 simdash")
    parser.add_argument("--config", help="the config file", default="config.json")
    args = parser.parse_args()

    with open(args.config, "r") as fid:
        config = json.load(fid)

    Dash(config).run()

