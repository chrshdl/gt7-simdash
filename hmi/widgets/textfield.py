from common.event import Event
from events import SYSTEM_PLAYSTATION_IP_CHANGED
from hmi.properties import Color, TextAlignment
from hmi.settings import POS

from . import EventDispatcher, Widget


class Textfield(Widget):
    def __init__(self, groups, w, h, mfs=38, text=""):
        super().__init__(groups, w, h, mfs)
        self.rect.center = POS["textfield"]
        self.text = text
        self.body_text = text
        self.body_text_alignment = TextAlignment.MIDBOTTOM
        self.body_text_color = Color.WHITE.rgb()
        self.header_color = Color.BLUE.rgb()
        self.header_text = "Enter Playstation IP"

    def handle_events(self, events):
        pass

    def append(self, txt):
        match txt:
            case "<":
                self.text = self.text[:-1]
            case "OK":
                EventDispatcher.dispatch(
                    Event(SYSTEM_PLAYSTATION_IP_CHANGED, self.text)
                )
                self.text = ""
            case _:
                self.text += txt
        self.body_text = self.text
