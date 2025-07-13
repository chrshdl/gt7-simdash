import pygame
from granturismo.model import Packet

from common.event import Event
from common.eventdispatcher import EventDispatcher
from events import HMI_VIEW_BUTTON_PRESSED, HMI_VIEW_BUTTON_RELEASED
from hmi.properties import Color


class View:
    def __init__(self):
        self.buttons = []
        self.screen = pygame.display.get_surface()
        self.sprite_group: pygame.sprite.Group = pygame.sprite.Group()

    def handle_view_events(self) -> None:
        for button in self.buttons:
            button.update()
            if button.is_pressed():
                EventDispatcher.dispatch(
                    Event(type=HMI_VIEW_BUTTON_PRESSED, data=button.text)
                )
            if button.is_released():
                EventDispatcher.dispatch(
                    Event(type=HMI_VIEW_BUTTON_RELEASED, data=button.text)
                )

    def handle_packet(self, packet: Packet):
        self.screen.fill(Color.BLACK.rgb())
        self.sprite_group.update(packet)
        self.sprite_group.draw(self.screen)

        for button in self.buttons:
            button.handle_packet(packet)
            button.render(self.screen)
