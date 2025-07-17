from os.path import join
from time import time
from typing import Optional

import pygame

from common.event import Event
from common.eventdispatcher import EventDispatcher
from events import WIDGET_NORMAL_SIZE
from hmi.properties import Color, ColorValues, TextAlignment


class Widget(pygame.sprite.Sprite):
    def __init__(
        self,
        groups: pygame.sprite.Group,
        w: int,
        h: int,
        mfs: int = 40,
        hfs: int = 46,
        animation_duration: float = 0.5,
        size_timeout: int = 8,
        size_factor: tuple = None,
    ):
        super().__init__(groups)
        self.header_text: Optional[str] = None
        self.header_color: ColorValues = Color.WHITE.rgb()
        self.body_text: Optional[str] = None
        self.body_text_color: ColorValues = Color.WHITE.rgb()
        self.body_text_alignment: TextAlignment = TextAlignment.MIDBOTTOM
        self.size_factor = size_factor
        self.w = w
        self.h = h
        self.mfs = mfs
        self.hfs = hfs

        self.normal_size, self.big_size = (w, h, mfs, hfs), (w, h, mfs, hfs)
        self._is_big = False
        self._size_timer_start: Optional[float] = None
        self.size_timeout = size_timeout

        self._animating = False
        self._animation_start_time: Optional[float] = None
        self._animation_duration = animation_duration
        self._from_size = self.normal_size
        self._to_size = self.big_size

        self.image = pygame.Surface((w, h)).convert()
        self.rect = self.image.get_rect(topleft=(0, 0))
        self.main_font = pygame.font.Font(join("fonts", "digital-7-mono.ttf"), mfs)
        self.header_font = pygame.font.Font(join("fonts", "pixeltype.ttf"), hfs)
        self.antialiased = False

    def on_big_size(self, event):
        self.size_factor = tuple(event.data)
        self.big_size = (
            int(self.w * self.size_factor[0]),
            int(self.h * self.size_factor[1]),
            int(self.mfs * self.size_factor[2]),
            int(self.hfs * self.size_factor[3]),
        )
        if not self._is_big:
            self._start_resize_animation(to_big=True)

    def on_normal_size(self, event):
        self.restore_normal_size()

    def _start_resize_animation(self, to_big: bool) -> None:
        self._from_size = self.big_size if not to_big else self.normal_size
        self._to_size = self.big_size if to_big else self.normal_size
        self._animation_start_time = time()
        self._animating = True

        if to_big:
            self._size_timer_start = time()
            self._is_big = True
        else:
            self._is_big = False
            self._size_timer_start = None

    def restore_normal_size(self):
        if self._is_big:
            self._start_resize_animation(to_big=False)

    def _interpolate_size(self, progress: float):
        def lerp(a, b, t):
            return int(a + (b - a) * t)

        w = lerp(self._from_size[0], self._to_size[0], progress)
        h = lerp(self._from_size[1], self._to_size[1], progress)
        mfs = lerp(self._from_size[2], self._to_size[2], progress)
        hfs = lerp(self._from_size[3], self._to_size[3], progress)
        return (w, h, mfs, hfs)

    def _set_size(self, w: int, h: int, mfs: int, hfs: int) -> None:
        self.image = pygame.Surface((w, h)).convert()
        self.rect = self.image.get_rect(center=self.rect.center)
        self.main_font = pygame.font.Font(join("fonts", "digital-7-mono.ttf"), mfs)
        self.header_font = pygame.font.Font(join("fonts", "pixeltype.ttf"), hfs)

    def draw_overlay(self, use_border: bool) -> None:
        pygame.draw.rect(self.image, Color.BLACK.rgb(), self.image.get_rect(), 0, 4)
        if use_border:
            pygame.draw.rect(self.image, Color.GREY.rgb(), self.image.get_rect(), 2, 4)

    def draw_header(self) -> None:
        if self.header_text is not None:
            width = self.image.get_rect().width // 2 + 2
            label = self.header_font.render(
                self.header_text, self.antialiased, self.header_color
            )
            self.image.blit(label, label.get_rect(midtop=(width, 6)))

    def draw_body(self) -> None:
        if self.body_text is not None:
            result = self.main_font.render(
                f"{self.body_text}", self.antialiased, self.body_text_color
            )
            if self.body_text_alignment == TextAlignment.CENTER:
                self.image.blit(
                    result, result.get_rect(center=self.image.get_rect().center)
                )
            elif self.body_text_alignment == TextAlignment.MIDBOTTOM:
                self.image.blit(
                    result, result.get_rect(midbottom=self.image.get_rect().midbottom)
                )

    def update(self, use_border: bool = True) -> None:
        if self._animating and self._animation_start_time is not None:
            elapsed = time() - self._animation_start_time
            progress = min(elapsed / self._animation_duration, 1.0)
            self._set_size(*self._interpolate_size(progress))
            if progress >= 1.0:
                self._animating = False

        # Auto-revert after timeout
        if self._is_big and self._size_timer_start is not None:
            if time() - self._size_timer_start >= self.size_timeout:
                EventDispatcher.dispatch(Event(WIDGET_NORMAL_SIZE, None))

        self.draw_overlay(use_border)
        self.draw_header()
        self.draw_body()
