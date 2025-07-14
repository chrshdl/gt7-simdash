import pygame
from granturismo.model import Packet

from hmi.properties import Color
from hmi.widgets.button import ButtonGroup


class View:
    def __init__(self):
        self.buttons = []
        self.screen = pygame.display.get_surface()
        self.sprite_group: pygame.sprite.Group = pygame.sprite.Group()
        self.button_group: ButtonGroup = ButtonGroup()

    def handle_view_events(self):
        self.screen.fill(Color.BLACK.rgb())
        self.button_group.update()
        self.button_group.render(self.screen)

    def handle_packet(self, packet: Packet):
        self.sprite_group.update(packet)
        self.sprite_group.draw(self.screen)
