import pygame

MAINMENU_START_PRESSED = pygame.event.custom_type()
MAINMENU_START_RELEASED = pygame.event.custom_type()
MAINMENU_SETTINGS = pygame.event.custom_type()
MAINMENU_SETTINGS_PRESSED = pygame.event.custom_type()
MAINMENU_SETTINGS_RELEASED = pygame.event.custom_type()

BACK_TO_MENU_PRESSED = pygame.event.custom_type()
BACK_TO_MENU_RELEASED = pygame.event.custom_type()

DROP_DOWN_PRESSED = pygame.event.custom_type()
DROP_DOWN_RELEASED = pygame.event.custom_type()
DROP_DOWN_SELECTED = pygame.event.custom_type()

ENTER_IP_OK_BUTTON_PRESSED = pygame.event.custom_type()
ENTER_IP_OK_BUTTON_RELEASED = pygame.event.custom_type()
ENTER_IP_KEYPAD_BUTTON_PRESSED = pygame.event.custom_type()
ENTER_IP_KEYPAD_BUTTON_RELEASED = pygame.event.custom_type()
ENTER_IP_DEL_BUTTON_PRESSED = pygame.event.custom_type()
ENTER_IP_DEL_BUTTON_RELEASED = pygame.event.custom_type()


CONNECTION_SUCCESS = pygame.event.custom_type()
CONNECTION_FAILED = pygame.event.custom_type()

BRIGHTNESS_DOWN_PRESSED = pygame.event.custom_type()
BRIGHTNESS_DOWN_RELEASED = pygame.event.custom_type()
BRIGHTNESS_UP_PRESSED = pygame.event.custom_type()
BRIGHTNESS_UP_RELEASED = pygame.event.custom_type()
