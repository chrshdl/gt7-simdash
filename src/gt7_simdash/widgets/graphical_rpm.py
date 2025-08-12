import pygame

from gt7_simdash.core.utils import load_font

from ..widgets.properties.colors import Color


class GraphicalRPM:
    def __init__(
        self,
        pos,
        alert_min,
        alert_max,
        max_rpm=9000,
        redline_rpm=8000,
        width=700,
        height=36,
        font_name=None,
    ):
        """
        pos: (x, y) center position of the widget
        alert_min: minimum RPM for alert (e.g. green->yellow transition)
        alert_max: maximum RPM for alert (e.g. redline)
        width: total width of the bar (in pixels)
        height: height of each tick (in pixels)
        """
        self.pos = pos
        self.min = 0
        self.alert_min = alert_min
        self.alert_max = alert_max
        self.max_rpm = max_rpm
        self.redline_rpm = redline_rpm
        self.width = width
        self.height = height
        self.current_rpm = 0

        self.ticks = int(max_rpm / 100)
        self.tick_width = int(width / self.ticks)
        self.small_font = load_font(36, font_name or "digital-7-mono")

    def update(self, rpm):
        self.current_rpm = int(rpm)

    def draw(self, surface):
        x_center, y = self.pos
        bar_left = x_center - self.width // 2
        for tick in range(self.ticks):
            tick_rpm = tick * (self.max_rpm / self.ticks)
            tick_x = bar_left + tick * self.tick_width
            color = Color.GREY.rgb()

            if tick_rpm < self.alert_min:
                color = Color.DARK_GREEN.rgb()
            elif tick_rpm < self.redline_rpm:
                color = Color.DARK_YELLOW.rgb()
            else:
                color = Color.RED.rgb()

            if tick_rpm <= self.current_rpm:
                rect = pygame.Rect(tick_x, y, self.tick_width - 1, self.height)
                pygame.draw.rect(surface, color, rect)
            else:
                rect = pygame.Rect(tick_x, y, self.tick_width - 1, self.height)
                pygame.draw.rect(surface, Color.GREY.rgb(), rect)
        # ticks
        tick_color = Color.LIGHT_GREY.rgb()
        for tick in range(self.ticks + 1):
            tick_x = bar_left + tick * self.tick_width
            y1 = y + self.height
            tick_rpm = tick * (self.max_rpm / self.ticks)
            if tick_rpm >= self.redline_rpm:
                tick_color = Color.LIGHT_RED.rgb()
            else:
                tick_color = Color.LIGHT_GREY.rgb()

            if tick % 10 == 0:
                y2 = y1 + 7
                width = 3
            else:
                y2 = y1 + 3
                width = 1
            pygame.draw.line(surface, tick_color, (tick_x, y1), (tick_x, y2), width)

        min_text = self.small_font.render(str(self.min), False, Color.LIGHT_GREY.rgb())
        surface.blit(min_text, (bar_left - 16, y + self.height + 2))
        max_text = self.small_font.render(
            str(self.max_rpm), False, Color.LIGHT_GREY.rgb()
        )
        surface.blit(max_text, (bar_left + self.width - 64, y + self.height + 2))
