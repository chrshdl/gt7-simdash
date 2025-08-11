import datetime
import sys

import pygame

from .states.main_menu_state import MainMenuState
from .states.state_manager import StateManager


def main() -> int:
    pygame.init()

    screen = pygame.display.set_mode((1024, 600))

    main_menu = MainMenuState()
    state_manager = StateManager(main_menu)
    main_menu.state_manager = state_manager

    clock = pygame.time.Clock()
    state_manager.running = True
    take_screenshot = False

    while state_manager.running:
        dt = clock.tick(60) / 1000  # 60 in fps, dt in seconds
        for pygame_event in pygame.event.get():
            if pygame_event.type == pygame.QUIT:
                state_manager.running = False
            elif pygame_event.type == pygame.KEYDOWN:
                if pygame_event.key == pygame.K_SPACE:
                    take_screenshot = True
            state_manager.handle_event(pygame_event)
        state_manager.update(dt)
        state_manager.draw(screen)
        pygame.display.flip()
        if take_screenshot:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"gt7-simdash_{timestamp}.png"
            pygame.image.save(screen.convert(24), filename)
            take_screenshot = False

    pygame.quit()
    return 0


if __name__ == "__main__":
    sys.exit(main())
