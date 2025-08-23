import pygame

from ..base.colors import Color
from .label import Label


class TextField(Label):
    def __init__(
        self,
        text,
        font,
        color,
        pos,
        width,
        height,
        *,
        antialias=True,
        border_color=Color.GREY.rgb(),
        background_color=Color.MEDIUM_GREY.rgb(),
        blinking_cursor=True,
    ):
        super().__init__(text, font, color, pos)
        self.width = width
        self.height = height
        self.border_color = border_color
        self.background_color = background_color
        self.rect = pygame.Rect(pos[0], pos[1], width, height)
        self.active = False

        self.cursor_position = len(text)
        self.cursor_visible = True
        self.cursor_timer = 0
        self.blinking_cursor = blinking_cursor
        self.antialias = antialias

    def update(self, dt):
        # Blink cursor every 0.5 s
        if self.blinking_cursor:
            self.cursor_timer += dt
            if self.cursor_timer >= 0.5:
                self.cursor_visible = not self.cursor_visible
                self.cursor_timer = 0

    def draw(self, surface):
        pygame.draw.rect(surface, self.background_color, self.rect, border_radius=4)
        # Draw border
        pygame.draw.rect(
            surface, self.border_color, self.rect, width=2, border_radius=4
        )
        # Render text left-aligned
        text_surf = self.font.render(self.text, self.antialias, self.color)
        text_rect = text_surf.get_rect()
        text_rect.topleft = (
            self.pos[0] + 10,
            self.pos[1] + (self.height - text_rect.height) // 2,
        )
        surface.blit(text_surf, text_rect)

        if self.cursor_visible:
            cursor_x = text_rect.left + self.font.size(self.text)[0]
            cursor_y = text_rect.top
            cursor_height = text_rect.height
            pygame.draw.line(
                surface,
                self.color,
                (cursor_x, cursor_y),
                (cursor_x, cursor_y + cursor_height),
                2,
            )

    def set_text(self, new_text):
        self.text = new_text
        self.cursor_position = min(self.cursor_position, len(new_text))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
        if self.active and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                if self.cursor_position > 0:
                    self.text = (
                        self.text[: self.cursor_position - 1]
                        + self.text[self.cursor_position :]
                    )
                    self.cursor_position -= 1
            elif event.key == pygame.K_DELETE:
                self.text = (
                    self.text[: self.cursor_position]
                    + self.text[self.cursor_position + 1 :]
                )
            elif event.key == pygame.K_LEFT:
                if self.cursor_position > 0:
                    self.cursor_position -= 1
            elif event.key == pygame.K_RIGHT:
                if self.cursor_position < len(self.text):
                    self.cursor_position += 1
            elif event.unicode and event.key != pygame.K_RETURN:
                self.text = (
                    self.text[: self.cursor_position]
                    + event.unicode
                    + self.text[self.cursor_position :]
                )
                self.cursor_position += 1
