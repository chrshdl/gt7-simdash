from enum import auto
from typing import Union

import pygame

EventType = Union[tuple[int, str], int]

SYSTEM_PLAYSTATION_IP_CHANGED: EventType = (auto(), "SYSTEM_PLAYSTATION_IP_CHANGED")
HMI_CONNECTION_ESTABLISHED: EventType = (auto(), "HMI_CONNECTION_ESTABLISHED")
HMI_CAR_CHANGED: EventType = (auto(), "HMI_CAR_CHANGED")
HMI_RPM_LEVEL_CHANGED: EventType = (auto(), "HMI_RPM_LEVEL_CHANGED")
RACE_NEW_LAP_STARTED: EventType = (auto(), "RACE_NEW_LAP_STARTED")
RACE_RETRY_STARTED: EventType = (auto(), "RACE_RETRY_STARTED")

HMI_VIEW_BUTTON_PRESSED: EventType = pygame.USEREVENT + 1
