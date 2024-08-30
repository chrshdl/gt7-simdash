from granturismo.intake import Feed

from common.event import Event
from common.eventdispatcher import EventDispatcher
from common.logger import Logger
from events import HMI_CONNECTION_ESTABLISHED
from hmi.properties import TextAlignment
from hmi.settings import POS

from . import Widget


class Connection(Widget):
    def __init__(self, groups, playstation_ip, w, h, mfs=40, hfs=46):
        super().__init__(groups, w, h, mfs, hfs)
        self.listener = Feed(playstation_ip)
        self.rect.center = POS["connection"]
        self.header_text = "Connecting, please wait..."
        self.body_text_alignment = TextAlignment.CENTER
        self.logger = Logger(self.__class__.__name__).get()

    def update(self, packet):
        super().update()

        self.send_handshake()

        try:
            packet = self.listener.get()
        except Exception as e:
            self.logger.info(f"💀 CONNECTION ISSUE: {e}")
        if packet is not None:
            EventDispatcher.dispatch(Event(HMI_CONNECTION_ESTABLISHED, self.listener))

    def send_handshake(self):
        if not self.listener._sock_bounded:
            self.listener.start()
        self.logger.info("🤝 SENDING HANDSHAKE...")
        self.listener.send_heartbeat()
