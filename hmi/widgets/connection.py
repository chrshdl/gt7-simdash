import time

import pygame
from granturismo.intake import Feed

from common.event import Event
from common.eventdispatcher import EventDispatcher
from common.logger import Logger
from events import HMI_CONNECTION_ESTABLISHED
from hmi.properties import Color, TextAlignment
from hmi.settings import POS

from . import Widget


class Connection(Widget):
    def __init__(
        self,
        groups: pygame.sprite.Group,
        playstation_ip: str,
        w: int,
        h: int,
        mfs: int = 40,
        hfs: int = 46,
    ):
        super().__init__(groups, w, h, mfs, hfs)
        self.listener = Feed(playstation_ip)
        self.rect.center = POS["connection"]
        self.header_color = Color.BLUE.rgb()
        self.header_text = "Connecting to Playstation"
        self.body_text = f"{playstation_ip}"
        self.body_text_alignment = TextAlignment.MIDBOTTOM
        self.logger = Logger(self.__class__.__name__).get()

        self._last_heartbeat_time = 0
        self._heartbeat_interval = 1

        self._dots_index = 0
        self._dots_frames = ["", ".", "..", "..."]
        self._last_animation_time = time.time()
        self._animation_interval = 0.5  # seconds

        self._connected = False
        self._cancelled = False

        self._host_unreachable = False
        self._last_host_check = 0.0
        self._host_check_interval = 5.0

    def update(self, _) -> None:
        super().update()

        if self._connected or self._cancelled:
            return

        now = time.time()

        if now - self._last_animation_time >= self._animation_interval:
            self._dots_index = (self._dots_index + 1) % len(self._dots_frames)
            self._last_animation_time = now

        dots = self._dots_frames[self._dots_index]
        self.header_text = f"Connecting to Playstation {dots}"

        if now - self._last_heartbeat_time >= self._heartbeat_interval:
            self.send_handshake()
            self._last_heartbeat_time = now

        try:
            packet = self.listener.get(blocking=False)
        except BlockingIOError:
            return
        except Exception as e:
            self.logger.info(f"💀 CONNECTION ISSUE: {e}")
            return

        if packet:
            self._connected = True
            self.logger.info("✅ Connected")
            EventDispatcher.dispatch(Event(HMI_CONNECTION_ESTABLISHED, self.listener))

    def send_handshake(self) -> None:
        current_time = time.time()

        if self._host_unreachable and (
            current_time - self._last_host_check < self._host_check_interval
        ):
            return

        if not self.listener._sock_bounded:
            self.listener.start()

        try:
            self.listener.send_heartbeat()
            # If successful, reset the unreachable flag
            self._host_unreachable = False
        except OSError as e:
            if e.errno == 65:
                self._host_unreachable = True
                self._last_host_check = current_time
                self.logger.warning("⚠️ No route to host — retrying in a few seconds...")
            else:
                self.logger.error(f"💀 Error while sending heartbeat: {e}")

    def cancel(self):
        self._cancelled = True
        self.listener.close()
        self.logger.info("❌ Cancelled")
