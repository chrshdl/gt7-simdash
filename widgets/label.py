import pygame


class Label:
    def __init__(
        self,
        text,
        font: pygame.font.Font,
        color: tuple[int, int, int],
        pos: tuple[int, int],
    ):
        self.font = font
        self.color = color
        self.text = text
        self.pos = pos

    def draw(self, surface):
        title = self.font.render(self.text, False, self.color)
        surface.blit(title, title.get_rect(center=self.pos))

    def set_text(self, text):
        self.text = text
