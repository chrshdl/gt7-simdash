import pygame
from enum import Enum


class Event(Enum):
    NEW_CAR_EVENT = (1, pygame.USEREVENT + 1)
    HMI_STARTED_EVENT = (2, pygame.USEREVENT + 2)

    def name(self):
        return self.value[1]
