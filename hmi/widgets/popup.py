import pygame
from hmi.settings import POS
from . import Widget
from hmi.properties import TextAlignment


class Popup(Widget):
    def __init__(self, groups, w, h, mfs=40, hfs=46, text=""):
        super().__init__(groups, w, h, mfs, hfs)
        self.popups = groups
        self.rect.center = POS["popup"]
        self.body_text_alignment = TextAlignment.CENTER
        self.header_text = text

    def update(self, packet):
        super().update()
        self.popups.draw(pygame.display.get_surface())
        pygame.display.update()

