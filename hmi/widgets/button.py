from enum import Enum, auto
from os.path import join

import pygame
from granturismo.model import Packet

from common.event import Event
from common.eventdispatcher import EventDispatcher
from common.logger import Logger
from hmi.properties import Color


class ButtonState(Enum):
    IDLE = auto()
    PRESSED = auto()
    RELEASED = auto()


class Button:
    def __init__(
        self,
        text: str,
        position: tuple[int, int],
        size: tuple[int, int] = (60, 50),
        font: pygame.font.Font = None,
        colors: dict[
            ButtonState,
            tuple[
                pygame.Color,  # top     \ for gradient
                pygame.Color,  # botton  /
                pygame.Color,  # border
                pygame.Color,  # text
            ],
        ] = None,
        out_events: dict[ButtonState, int] = None,
    ):
        self.text: str = text
        self.position: tuple[int, int] = position
        self.size: tuple[int, int] = size
        self.button: pygame.Surface = pygame.Surface(size).convert()
        self.rect = self.button.get_rect(topleft=position)
        self.state = ButtonState.IDLE
        self.prev_state = ButtonState.IDLE
        self.border_thickness = 2
        self.border_radius = 4

        self.colors = {
            ButtonState.IDLE: (
                pygame.Color(Color.BLACK.rgb()),
                pygame.Color(Color.BLACK.rgb()),
                pygame.Color(Color.GREY.rgb()),
                pygame.Color(Color.WHITE.rgb()),
            ),
            ButtonState.PRESSED: (
                pygame.Color(Color.DARK_BLUE.rgb()),
                pygame.Color(Color.DARKEST_BLUE.rgb()),
                pygame.Color(Color.BLUE.rgb()),
                pygame.Color(Color.WHITE.rgb()),
            ),
            ButtonState.RELEASED: (
                pygame.Color(Color.BLACK.rgb()),
                pygame.Color(Color.BLACK.rgb()),
                pygame.Color(Color.GREY.rgb()),
                pygame.Color(Color.WHITE.rgb()),
            ),
        }

        self.out_events = {}

        if colors:
            self.colors.update(colors)

        self.font = font or pygame.font.Font(
            join("fonts", "pixeltype.ttf"),
            50,
        )

        if out_events:
            self.out_events.update(out_events)

        self.logger = Logger(self.__class__.__name__).get()

    def update(self):
        is_inside = self.rect.collidepoint(pygame.mouse.get_pos())
        is_pressed = pygame.mouse.get_pressed()[0]

        self.prev_state = self.state

        if is_pressed and is_inside:
            if self.state != ButtonState.PRESSED:
                EventDispatcher.dispatch(
                    Event(type=self.out_events[ButtonState.PRESSED], data=self.text)
                )
            self.state = ButtonState.PRESSED

        elif not is_pressed and self.prev_state == ButtonState.PRESSED and is_inside:
            EventDispatcher.dispatch(
                Event(type=self.out_events[ButtonState.RELEASED], data=self.text)
            )
            self.state = ButtonState.RELEASED
        else:
            self.state = ButtonState.IDLE

    def handle_packet(self, packet: Packet):
        if self.text == "TCS":
            if packet.flags.tcs_active:
                self.gradient = True
                self.top = pygame.Color(Color.DEEP_PURPLE.rgb())
                self.gradient_outline_color = Color.MEDIUM_PURPLE.rgb()
            if not packet.flags.tcs_active:
                self.gradient = False
        if self.text == "LIGHTS":
            if packet.flags.lights_active:
                self.gradient = True
                self.top = pygame.Color(Color.DARK_GREEN.rgb())
                self.gradient_outline_color = Color.GREEN.rgb()
            if not packet.flags.lights_active:
                self.gradient = False
        if self.text == "HIBEAM":
            if packet.flags.lights_high_beams_active:
                self.gradient = True
                self.top = pygame.Color(0, 50, 124)
                self.gradient_outline_color = Color.BLUE.rgb()
            if not packet.flags.lights_high_beams_active:
                self.gradient = False

    def is_pressed(self):
        return self.state == ButtonState.PRESSED

    def is_released(self):
        return self.state == ButtonState.RELEASED

    def render(self, display: pygame.Surface):
        pos_x = self.position[0] - self.border_thickness
        pos_y = self.position[1] - self.border_thickness
        size_x = self.size[0] + self.border_thickness * 2
        size_y = self.size[1] + self.border_thickness * 2

        (
            top_color,
            bottom_color,
            border_color,
            text_color,
        ) = self.colors[self.state]
        self._draw_gradient(top_color, bottom_color)
        pygame.draw.rect(
            display,
            border_color,
            (pos_x, pos_y, size_x, size_y),
            self.border_thickness,
            self.border_radius,
        )
        text_surf = self.font.render(f"{self.text}", False, text_color)
        text_rect = text_surf.get_rect(
            center=(
                self.position[0] + self.rect.width // 2,
                self.position[1] + self.rect.height // 2 + 4,
            )
        )
        display.blit(self.button, self.position)
        display.blit(text_surf, text_rect)

    def _draw_gradient(self, top: pygame.Color, bottom: pygame.Color):
        for y in range(self.rect.height):
            ratio = y / self.rect.height
            r = top.r + (bottom.r - top.r) * ratio
            g = top.g + (bottom.g - top.g) * ratio
            b = top.b + (bottom.b - top.b) * ratio
            a = top.a + (bottom.a - top.a) * ratio
            pygame.draw.line(
                self.button,
                (int(r), int(g), int(b), int(a)),
                (0, y),
                (self.rect.width, y),
            )
