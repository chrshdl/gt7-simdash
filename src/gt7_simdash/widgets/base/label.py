import pygame

from ...widgets.base.colors import Color


class Label:
    def __init__(
        self,
        text,
        font: pygame.font.Font = None,
        color: tuple[int, int, int] = Color.WHITE.rgb(),
        pos: tuple[int, int] = (0, 0),
        center: bool = True,
        antialias: bool = True,
    ):
        self.text = text
        self.font = font
        self.color = color
        self.pos = pos
        self.center = center
        self.antialias = antialias
        self._render_text()

    def _render_text(self):
        """Render and cache the surface whenever text changes."""
        self.surface = self.font.render(self.text, self.antialias, self.color)
        if self.center:
            self.rect = self.surface.get_rect(center=self.pos)
        else:
            self.rect = self.surface.get_rect(topleft=self.pos)

    def set_text(self, text: str):
        """Update the text and re-render."""
        if text != self.text:
            self.text = text
            self._render_text()

    def draw(self, surface: pygame.Surface):
        surface.blit(self.surface, self.rect)
