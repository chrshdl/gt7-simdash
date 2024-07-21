import pygame
import sys
from hmi import HMI
from event import Event


class Dash:
    def __init__(self, conf):
        self.W = conf["width"]
        self.H = conf["height"]
        fullscreen = conf["fullscreen"]
        self.ip_address = conf["ps5_ip"]

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

        hmi = HMI()
        hmi.start()

        import time
        from unittest.mock import Mock

        while True:
            for event in pygame.event.get():
                if event.type == Event.NEW_CAR_EVENT.name():
                    hmi.set_rpm_alerts(packet.rpm_alert.min, packet.rpm_alert.max)

                if event.type == Event.HMI_STARTED_EVENT.name():

                    hmi.draw_text("Initializing, please wait...")
                    time.sleep(3)

                    if self.ip_address is not None:
                        from granturismo.intake import Feed

                        listener = Feed(self.ip_address)
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
            hmi.run(packet)
            pygame.display.flip()
            self.clock.tick(60)
