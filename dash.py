import pygame
import sys
from hmi.hmi import HMI
from hmi.event import Event
import argparse
import json
import logging


class Dash:
    def __init__(self, conf):
        self.W = conf["width"]
        self.H = conf["height"]
        fullscreen = conf["fullscreen"]
        ps5_ip = conf["ps5_ip"]
        debug_mode = conf["debug_mode"]

        logging.basicConfig()
        logging.getLogger().setLevel(logging.DEBUG)
        self.logger = logging.getLogger(self.__class__.__name__)

        pygame.init()
        self.clock = pygame.time.Clock()

        monitor_size = (
            pygame.display.Info().current_w,
            pygame.display.Info().current_h,
        )
        if not fullscreen:
            pygame.display.set_mode((self.W, self.H), pygame.RESIZABLE)
        else:
            pygame.display.set_mode(monitor_size, pygame.FULLSCREEN)

        self.hmi = HMI(ps5_ip, debug_mode)

    def close(self):
        pygame.quit()
        sys.exit()

    def _update_packet(self, packet):
        packet.engine_rpm = (packet.engine_rpm + 50) % packet.rpm_alert.max
        if packet.engine_rpm >= packet.rpm_alert.min:
            packet.flags.rev_limiter_alert_active = True
        else:
            packet.flags.rev_limiter_alert_active = False
            if packet.engine_rpm < 50:
                packet.current_gear = (packet.current_gear + 1) % 7
        packet.car_speed = (packet.car_speed + 0.1) % (260 / 3.6)
        return packet

    def run(self):

        self.hmi.start()

        import time
        from unittest.mock import Mock

        while True:
            for event in pygame.event.get():
                if event.type == Event.NEW_CAR_EVENT.type():
                    self.logger.info(
                        f"received {Event.NEW_CAR_EVENT.name()}, car_id changed to: {event.message}"
                    )
                    self.hmi.set_rpm_alerts(packet.rpm_alert.min, packet.rpm_alert.max)

                if event.type == Event.HMI_STARTED_EVENT.type():
                    self.logger.info(
                        f"received {Event.HMI_STARTED_EVENT.name()}, initializing HMI: {event.message}"
                    )
                    self.hmi.draw_text("Initializing, please wait...")

                    time.sleep(3)

                    if self.hmi.ps5_ip is not None:
                        from granturismo.intake import Feed

                        listener = Feed(self.ps5_ip)
                        listener.start()
                        packet = listener.get()
                    else:
                        from unittest.mock import Mock, MagicMock

                        packet = Mock()
                        packet.car_speed = 0 / 3.6
                        packet.current_gear = 1
                        packet.engine_rpm = 900.0
                        packet.rpm_alert.min = 7800
                        packet.rpm_alert.max = 8000
                        packet.flags.rev_limiter_alert_active = False
                        packet.last_lap_time = 165256
                        packet.best_lap_time = None
                        packet.flags.paused = False
                        packet.flags.car_on_track = True
                        packet.flags.loading_or_processing = False
                        packet.lap_count = 1
                        packet.laps_in_race = 3
                        packet.car_id = 203

                        listener = Mock()
                        listener.get = MagicMock(name="get")
                        listener.get.return_value = packet
                        listener.close = MagicMock(name="close")

                if event.type == pygame.QUIT:
                    listener.close()
                    self.close()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        listener.close()
                        self.close()
                    if event.key == pygame.K_SPACE:
                        screenshot = pygame.Surface((self.W, self.H))
                        screenshot.blit(pygame.display.get_surface(), (0, 0))
                        pygame.image.save(screenshot, "gt7-simdash.png")
            if isinstance(packet, Mock):
                packet = self._update_packet(packet)
            else:
                packet = listener.get()
            self.hmi.run(packet)
            pygame.display.flip()
            self.clock.tick(60)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="PS5 sim dash")
    parser.add_argument("--config", help="json with the config", default="config.json")
    args = parser.parse_args()

    with open(args.config, "r") as fid:
        config = json.load(fid)

    dash = Dash(config)
    dash.run()
