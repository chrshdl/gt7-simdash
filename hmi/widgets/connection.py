import pygame
from granturismo.intake import Feed
from granturismo.model import Packet

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
        self.header_text = "Connecting to ..."
        self.body_text = f"{playstation_ip}"
        self.body_text_alignment = TextAlignment.MIDBOTTOM
        self.logger = Logger(self.__class__.__name__).get()

    def update(self, _) -> None:  # type: ignore
        super().update()

        self.send_handshake()

        try:
            packet: Packet = self.listener.get()
        except Exception as e:  # noqa: S110
            self.logger.info(f"💀 CONNECTION ISSUE: {e}")
        else:
            if packet is not None:
                EventDispatcher.dispatch(
                    Event(HMI_CONNECTION_ESTABLISHED, self.listener)
                )

    def send_handshake(self) -> None:
        if not self.listener._sock_bounded:
            self.listener.start()
        # self.logger.info("🤝 SENDING HANDSHAKE...")
        self.listener.send_heartbeat()
