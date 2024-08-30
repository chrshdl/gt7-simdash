from enum import auto

import pygame

EventType = tuple[int, str]

SYSTEM_PLAYSTATION_IP_CHANGED: EventType = (auto(), "SYSTEM_PLAYSTATION_IP_CHANGED")
HMI_CONNECTION_ESTABLISHED: EventType = (auto(), "HMI_CONNECTION_ESTABLISHED")
HMI_CAR_CHANGED: EventType = (auto(), "HMI_CAR_CHANGED")
HMI_RPM_LEVEL_CHANGED: EventType = (auto(), "HMI_RPM_LEVEL_CHANGED")
RACE_NEW_LAP_STARTED: EventType = (auto(), "RACE_NEW_LAP_STARTED")
RACE_RETRY_STARTED: EventType = (auto(), "RACE_RETRY_STARTED")

HMI_VIEW_BUTTON_PRESSED: int = pygame.USEREVENT + 1
