import pygame

from gt7_simdash.core.utils import FontFamily, load_font

from ..base.button import AbstractButton
from ..base.colors import Color


class Dropdown(AbstractButton):
    def __init__(
        self,
        rect,
        options,
        selected_index,
        event_type_pressed,
        event_type_released,
        event_type_select,
    ):
        super().__init__(rect, event_type_pressed, event_type_released)
        self.options = options
        self.selected_index = selected_index
        self.open = False
        self.event_type_select = event_type_select
        self.pressed_option_index = None

    def handle_event(self, event):
        option_rects = self.get_option_rects() if self.open else []

        if self.open:
            if event.type == pygame.MOUSEBUTTONDOWN:
                for i, option_rect in enumerate(option_rects):
                    if option_rect.collidepoint(event.pos):
                        self.pressed_option_index = i
                        # Optionally, give visual feedback here
                        return
                # click outside closes dropdown
                if not self.rect.collidepoint(event.pos):
                    self.open = False
                    self.pressed_option_index = None

            elif event.type == pygame.MOUSEBUTTONUP:
                if self.pressed_option_index is not None:
                    option_rect = option_rects[self.pressed_option_index]
                    if option_rect.collidepoint(event.pos):
                        self.selected_index = self.pressed_option_index
                        self.open = False
                        pygame.event.post(
                            pygame.event.Event(
                                self.event_type_select,
                                {
                                    "selected_index": self.selected_index,
                                    "resolution": self.options[self.selected_index],
                                },
                            )
                        )
                    self.pressed_option_index = None

        super().handle_event(event)
        if event.type == pygame.MOUSEBUTTONUP and self.rect.collidepoint(event.pos):
            if self.is_pressed:
                self.open = not self.open
                self.pressed_option_index = None

    def draw(self, surface):
        color = Color.BLUE.rgb() if self.open else Color.GREY.rgb()
        pygame.draw.rect(surface, color, self.rect, width=2, border_radius=4)
        font = load_font(40, name=FontFamily.PIXEL_TYPE)
        text = f"{self.options[self.selected_index][0]} x {self.options[self.selected_index][1]}"
        text_surf = font.render(text, False, Color.WHITE.rgb())
        text_rect = text_surf.get_rect(midleft=(self.rect.x + 15, self.rect.centery))
        surface.blit(text_surf, text_rect)
        pygame.draw.polygon(
            surface,
            Color.WHITE.rgb(),
            [
                (self.rect.right - 35, self.rect.centery - 8),
                (self.rect.right - 15, self.rect.centery - 8),
                (self.rect.right - 25, self.rect.centery + 8),
            ],
        )
        if self.open:
            option_rects = self.get_option_rects()
            for i, option_rect in enumerate(option_rects):
                if self.pressed_option_index == i:
                    bg_color = Color.LIGHT_GREY.rgb()
                elif i == self.selected_index:
                    bg_color = Color.GREY.rgb()
                else:
                    bg_color = Color.DARK_GREY.rgb()
                pygame.draw.rect(
                    surface, bg_color, option_rect, width=0, border_radius=0
                )
                option_text = f"{self.options[i][0]} x {self.options[i][1]}"
                option_surf = font.render(option_text, False, Color.WHITE.rgb())
                option_text_rect = option_surf.get_rect(
                    midleft=(option_rect.x + 15, option_rect.centery)
                )
                surface.blit(option_surf, option_text_rect)

    def get_option_rects(self):
        rects = []
        x, y, w, h = self.rect
        for i in range(len(self.options)):
            rects.append(pygame.Rect(x, y + (i + 1) * h, w, h))
        return rects
