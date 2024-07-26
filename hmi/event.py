import pygame
from enum import Enum


class Event(Enum):
    HMI_DASH_STARTED = (1, pygame.USEREVENT + 1, "HMI_DASH_STARTED")
    HMI_CAR_CHANGED = (2, pygame.USEREVENT + 2, "HMI_CAR_CHANGED")
    HMI_RPM_LEDS_CHANGED = (3, pygame.USEREVENT + 3, "HMI_RPM_LEDS_CHANGED")

    def type(self):
        return self.value[1]

    def name(self):
        return self.value[2]
