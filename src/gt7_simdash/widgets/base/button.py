from enum import Enum, auto

import pygame

from gt7_simdash.core.utils import FontFamily, load_font

from ..properties.colors import Color


class ButtonState(Enum):
    IDLE = auto()
    PRESSED = auto()
    RELEASED = auto()


class AbstractButton:
    def __init__(
        self,
        rect,
        event_type_pressed: pygame.event.EventType,
        event_type_released: pygame.event.EventType,
        event_data=None,
    ):
        self.rect = pygame.Rect(rect)
        self.event_type_pressed = event_type_pressed
        self.event_type_released = event_type_released
        self.event_data = event_data or {}

        self.state = ButtonState.IDLE

        # Track which pointer currently "owns" the press:
        # - None: no active press
        # - 0: mouse
        # - finger_id (int): specific touch finger
        self._active_pointer = None

    def draw(self, surface):
        raise NotImplementedError("draw() must be overridden.")

    def is_pressed(self):
        return self.state == ButtonState.PRESSED

    def is_released(self):
        return self.state == ButtonState.RELEASED

    @staticmethod
    def _screen_size():
        surf = pygame.display.get_surface()
        return surf.get_size() if surf else (0, 0)

    @staticmethod
    def _event_xy(event):
        """
        Return pixel (x, y) for either mouse or touch events.
        - MOUSE*  -> event.pos
        - FINGER* -> (event.x * w, event.y * h)
        """
        if event.type in (
            pygame.MOUSEBUTTONDOWN,
            pygame.MOUSEBUTTONUP,
            pygame.MOUSEMOTION,
        ):
            return event.pos
        if event.type in (pygame.FINGERDOWN, pygame.FINGERUP, pygame.FINGERMOTION):
            w, h = AbstractButton._screen_size()
            return int(event.x * w), int(event.y * h)
        return None

    def is_inside_xy(self, x, y):
        return self.rect.collidepoint(x, y)

    def is_inside(self, event):
        xy = self._event_xy(event)
        return False if xy is None else self.is_inside_xy(*xy)

    def handle_event(self, event):
        # Normalize to a "pointer id":
        # - mouse -> 0
        # - touch -> event.finger_id
        if event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP):
            pid = 0
        elif event.type in (pygame.FINGERDOWN, pygame.FINGERUP):
            pid = getattr(event, "finger_id", None)
        else:
            return

        if event.type in (pygame.MOUSEBUTTONDOWN, pygame.FINGERDOWN):
            if self.is_inside(event):
                if self.state != ButtonState.PRESSED:
                    pygame.event.post(
                        pygame.event.Event(self.event_type_pressed, self.event_data)
                    )
                self.state = ButtonState.PRESSED
                self._active_pointer = pid

        elif event.type in (pygame.MOUSEBUTTONUP, pygame.FINGERUP):
            if self.state == ButtonState.PRESSED and self._active_pointer == pid:
                if self.is_inside(event):
                    pygame.event.post(
                        pygame.event.Event(self.event_type_released, self.event_data)
                    )
                    self.state = ButtonState.RELEASED
                else:
                    self.state = ButtonState.IDLE
                self._active_pointer = None


class ButtonGroup:
    def __init__(self):
        self.buttons: list[AbstractButton] = []

    def add(self, button: AbstractButton):
        self.buttons.append(button)

    def extend(self, buttons: list[AbstractButton]):
        self.buttons.extend(buttons)

    def handle_event(self, event):
        for button in self.buttons:
            button.handle_event(event)

    def draw(self, display: pygame.Surface):
        for button in self.buttons:
            button.draw(display)


class Button(AbstractButton):
    def __init__(
        self,
        rect,
        text,
        event_type_pressed,
        event_type_released,
        event_data=None,
        font=None,
        color=None,
    ):
        super().__init__(rect, event_type_pressed, event_type_released, event_data)
        if event_data is None:
            event_data = {"label": text}
            self.event_data = event_data
        self.text = text
        self.font = font or load_font(32, FontFamily.DIGITAL_7_MONO)

        self.color = color or Color.WHITE.rgb()

    def draw(self, surface):
        border_color = (
            Color.BLUE.rgb()
            if self.is_pressed() and self.color == Color.WHITE.rgb()
            else self.color
            if self.is_pressed() and self.color
            else Color.GREY.rgb()
        )
        pygame.draw.rect(surface, border_color, self.rect, width=2, border_radius=4)
        text_surf = self.font.render(self.text, False, self.color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)
