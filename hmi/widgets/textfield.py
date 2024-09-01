import pygame

from common.event import Event
from events import SYSTEM_PLAYSTATION_IP_CHANGED
from hmi.properties import Color, TextAlignment
from hmi.settings import POS

from . import EventDispatcher, Widget


class Textfield(Widget):
    def __init__(
        self, groups: pygame.sprite.Group, w: int, h: int, mfs: int = 38, text: str = ""
    ):
        super().__init__(groups, w, h, mfs)
        self.rect.center = POS["textfield"]
        self.text: str = text
        self.body_text = text
        self.body_text_alignment = TextAlignment.MIDBOTTOM
        self.body_text_color = Color.WHITE.rgb()
        self.header_color = Color.BLUE.rgb()
        self.header_text = "Enter Playstation IP"

    def handle_events(self, _):
        pass

    def append(self, txt: str) -> None:
        match txt:
            case "<":
                self.text = self.text[:-1]
            case "OK":
                EventDispatcher.dispatch(
                    Event(SYSTEM_PLAYSTATION_IP_CHANGED, self.text)
                )
                self.text = ""
            case x if len(x) >= 7:
                self.text = txt
            case _:
                self.text += txt
        self.body_text = self.text
