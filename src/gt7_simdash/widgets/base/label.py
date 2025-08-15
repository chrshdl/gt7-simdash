import pygame

from gt7_simdash.core.utils import load_font


class Label:
    def __init__(
        self,
        text: str,
        font_name: str,
        font_size: int,
        color: tuple[int, int, int],
        pos: tuple[int, int],
        center: bool = True,
    ):
        self.font = load_font(font_size, font_name)
        self.color = color
        self.pos = pos
        self.center = center

        self.text = text
        self._render_text()

    def _render_text(self):
        """Render and cache the surface whenever text changes."""
        self.surface = self.font.render(self.text, False, self.color)
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
