from enum import auto

import pygame

EventType = tuple[int, str]

# Specific events for state changes
SYSTEM_PLAYSTATION_IP_CHANGED: EventType = (auto(), "SYSTEM_PLAYSTATION_IP_CHANGED")
HMI_CONNECTION_ESTABLISHED: EventType = (auto(), "HMI_CONNECTION_ESTABLISHED")
HMI_CAR_CHANGED: EventType = (auto(), "HMI_CAR_CHANGED")
HMI_RPM_LEVEL_CHANGED: EventType = (auto(), "HMI_RPM_LEVEL_CHANGED")
RACE_NEW_LAP_STARTED: EventType = (auto(), "RACE_NEW_LAP_STARTED")
RACE_RETRY_STARTED: EventType = (auto(), "RACE_RETRY_STARTED")

# Specific events for buttons in view "Startup"
HMI_STARTUP_BACK_BUTTON_PRESSED: int = pygame.USEREVENT + 1
HMI_STARTUP_BACK_BUTTON_RELEASED: int = pygame.USEREVENT + 2

# Specific events for buttons in view "Wizard"
HMI_WIZARD_OK_BUTTON_PRESSED: int = pygame.USEREVENT + 3
HMI_WIZARD_OK_BUTTON_RELEASED: int = pygame.USEREVENT + 4
HMI_WIZARD_DEL_BUTTON_PRESSED: int = pygame.USEREVENT + 5
HMI_WIZARD_DEL_BUTTON_RELEASED: int = pygame.USEREVENT + 6
HMI_WIZARD_KEYPAD_BUTTON_PRESSED: int = pygame.USEREVENT + 7
HMI_WIZARD_KEYPAD_BUTTON_RELEASED: int = pygame.USEREVENT + 8
