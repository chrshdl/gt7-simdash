from hmi.color import Color
from hmi.widget import AbstractWidget


class GearIndicator(AbstractWidget):
    #    def __init__(self, w, h, x, y):
    #        super().__init__()
    #        self.image = pygame.Surface((w, h)).convert()
    #        self.rect = self.image.get_rect(center=(x, y))
    #        self.font = pygame.font.Font("fonts/digital-7-mono.ttf", 240)

    # def draw_overlay(self):
    #    pygame.draw.rect(self.image, Color.DARK_GREY.rgb(), self.image.get_rect(), 0, 4)
    #    pygame.draw.rect(self.image, Color.GREY.rgb(), self.image.get_rect(), 1, 4)

    def update(self, data):
        super().update(data)
        if not data.flags.in_gear:
            gear = "N"
        else:
            if data.current_gear == 0:
                gear = "R"
            elif data.current_gear == None:
                gear = "N"
            else:
                gear = str(data.current_gear)
        if data.flags.rev_limiter_alert_active:
            color = Color.LIGHT_RED.rgb()
        else:
            color = Color.WHITE.rgb()
        gear_render = self.primary_font.render(f"{gear}", False, color)
        self.image.blit(
            gear_render, gear_render.get_rect(center=self.image.get_rect().center)
        )
