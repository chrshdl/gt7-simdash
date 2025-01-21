import sys
from typing import Any
from unittest.mock import Mock

import pygame
from common.event import Event
from common.eventdispatcher import EventDispatcher
from common.logger import Logger
from configs import Config, ConfigManager
from events import (
    HMI_CAR_CHANGED,
    HMI_CONNECTION_ESTABLISHED,
    HMI_VIEW_BUTTON_PRESSED,
    HMI_VIEW_BUTTON_RELEASED,
    SYSTEM_PLAYSTATION_IP_CHANGED,
)
from hmi.views.dashboard import Dashboard
from hmi.views.startup import Startup
from hmi.views.wizard import Wizard


class Main:
    HEARTBEAT_DELAY = 9

    STATE_STARTUP = "STARTUP"
    STATE_DASHBOARD = "DASHBOARD"
    STATE_SETUP = "SETTINGS"

    def __init__(self, conf: Config):
        self.w = conf.width
        self.h = conf.height
        fullscreen = conf.fullscreen
        self.playstation_ip = conf.playstation_ip

        self.listener = None
        self.running = False
        self._car_id = -1

        pygame.init()

        monitor_size = (
            pygame.display.Info().current_w,
            pygame.display.Info().current_h,
        )
        if not fullscreen:
            pygame.display.set_mode((self.w, self.h), pygame.RESIZABLE)
        else:
            pygame.display.set_mode(monitor_size, pygame.FULLSCREEN)

        self.states: dict[str, Any] = {}
        self.states.update({Main.STATE_DASHBOARD: Dashboard()})
        self.states.update({Main.STATE_SETUP: Wizard(conf.recent_connected)})

        self.state = Main.STATE_DASHBOARD

        self.logger = Logger(self.__class__.__name__).get()

        EventDispatcher.add_listener(HMI_CONNECTION_ESTABLISHED, self.on_connection)
        EventDispatcher.add_listener(SYSTEM_PLAYSTATION_IP_CHANGED, self.on_ip_changed)

    def run(self):
        self.running = True
        clock = pygame.time.Clock()
        packet = None
        last_heartbeat = 0

        while self.running:
            clock.tick(30)

            if self.listener is not None:
                try:
                    packet = self.listener.get()
                except Exception as e:
                    self.logger.info(f"💀 CONNECTION ISSUE: {e}")
                    self.state = Main.STATE_STARTUP

                if packet.received_time - last_heartbeat >= Main.HEARTBEAT_DELAY:
                    last_heartbeat = packet.received_time
                    self.logger.info("💗")
                    self.listener.send_heartbeat()
            else:
                if packet is None:
                    packet = self.get_mock_packet()

            events: list[pygame.event.Event] = pygame.event.get()

            for event in events:
                if event.type == HMI_VIEW_BUTTON_PRESSED:
                    self.logger.info(f"Button {event.message} was pressed")
                if event.type == HMI_VIEW_BUTTON_RELEASED:
                    self.logger.info(f"Button {event.message} was released")
                    if event.message == "Setup":
                        self.state = Main.STATE_SETUP
                    if event.message == "BACK":
                        self.state = Main.STATE_DASHBOARD

                if event.type == pygame.QUIT:
                    self.running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                    if event.key == pygame.K_SPACE:
                        screenshot = pygame.Surface((self.w, self.h))
                        screenshot.blit(pygame.display.get_surface(), (0, 0))
                        pygame.image.save(screenshot, "gt7-simdash.png")

            self.states[self.state].handle_events(events)
            self.states[self.state].update(packet)
            self.car_id(packet)
            pygame.display.update()

        self.close()

    def get_mock_packet(self):
        packet = Mock()
        packet.car_speed = 0/3.6
        packet.car_max_speed = 200
        packet.current_gear = 0
        packet.flags.in_gear = packet.current_gear > 0 
        packet.engine_rpm = 0.0
        packet.rpm_alert.min = 6000
        packet.rpm_alert.max = 7000
        packet.flags.rev_limiter_alert_active = False
        packet.flags.tcs_active = False
        packet.flags.lights_active = False
        packet.flags.lights_high_beams_active = False
        packet.last_lap_time = 10
        packet.lap_count = -1
        packet.laps_in_race = -1
        packet.best_lap_time = 10
        packet.current_lap_time = 10
        packet.position.x = 0
        packet.position.z = 0
        return packet

    def close(self):
        if self.listener is not None:
            self.listener.close()
        pygame.quit()
        sys.exit()

    def car_id(self, packet):
        if packet is not None:
            if self._car_id != packet.car_id:
                self._car_id = packet.car_id
                data = (packet.rpm_alert.min, packet.rpm_alert.max)
                EventDispatcher.dispatch(Event(HMI_CAR_CHANGED, data))

    def on_connection(self, event):
        ConfigManager.last_connected(self.playstation_ip)  # type: ignore
        self.state = Main.STATE_DASHBOARD
        self.listener = event.data

    def on_ip_changed(self, event):
        self.playstation_ip = event.data
        self.states.update({Main.STATE_STARTUP: Startup(self.playstation_ip)})
        self.states.update({Main.STATE_DASHBOARD: Dashboard()})
        self.state = Main.STATE_STARTUP


if __name__ == "__main__":
    import argparse
    from pathlib import Path

    parser = argparse.ArgumentParser(description="Gran Turismo 7 simdash")
    parser.add_argument("--config", help="the config file", default=None)
    args = parser.parse_args()

    EventDispatcher()

    if args.config:
        ConfigManager.set_path(Path(args.config))
    config = ConfigManager.get_config()
    Main(config).run()
