from hmi.color import Color
from hmi.widget import AbstractWidget


class InitializingScreen(AbstractWidget):
    def update(self, data):
        data_render = self.recondary_font.render(data, True, Color.WHITE.rgb())
        center = self.image.get_rect().center
        self.image.blit(data_render, data_render.get_rect(center=center))
