import pygame
from enum import Enum


class Event(Enum):
    NEW_CAR_EVENT = (1, pygame.USEREVENT + 1, "NEW_CAR_EVENT")
    HMI_STARTED_EVENT = (2, pygame.USEREVENT + 2, "HMI_STARTED_EVENT")
    LEDS_SHOW = (3, pygame.USEREVENT + 3, "LEDS_SHOW")
    LEDS_CLEAR_ALL = (4, pygame.USEREVENT + 4, "LEDS_CLEAR_ALL")

    def type(self):
        return self.value[1]

    def name(self):
        return self.value[2]
