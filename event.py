import pygame
from enum import Enum


class Event(Enum):
    NEW_CAR_EVENT = (1, pygame.USEREVENT + 1)

    def name(self):
        return self.value[1]
