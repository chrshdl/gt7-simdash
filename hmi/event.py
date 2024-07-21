import pygame
from enum import Enum


class Event(Enum):
    NEW_CAR_EVENT = (1, pygame.USEREVENT + 1, "NEW_CAR_EVENT")
    HMI_STARTED_EVENT = (2, pygame.USEREVENT + 2, "HMI_STARTED_EVENT")

    def type(self):
        return self.value[1]

    def name(self):
        return self.value[2]
