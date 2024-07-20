import pygame
from color import Color


class RPM(pygame.sprite.Sprite):
    def __init__(self, screen_width, y, rpm_alert_min, rpm_alert_max, step):
        super().__init__()
        self.rpm_alert_min = rpm_alert_min
        self.rpm_alert_max = rpm_alert_max
        self.rpm_alert_min_thres = (
            int(self.rpm_alert_min - self.rpm_alert_max * 0.04) // 100
        )
        margin = 1
        w = 3
        h = 35
        offset_center = (screen_width - rpm_alert_max * (margin + w)) // 2
        pos = ((offset_center + (margin + w) * step + margin), y)
        self.step = step
        if self.step % 10 == 0:
            self.image = pygame.Surface((w, h + 7)).convert()
        else:
            self.image = pygame.Surface((w, h)).convert()
        self.rect = self.image.get_rect(topleft=pos)

    def update(self, current_rpm):
        if self.step <= current_rpm:
            if (
                current_rpm >= self.rpm_alert_min_thres
                and self.step >= self.rpm_alert_min_thres
            ):
                self.image.fill(Color.RED.rgb())
            else:
                self.image.fill(Color.BLUE.rgb())
        else:
            if self.step >= self.rpm_alert_min_thres:
                self.image.fill(Color.DARK_RED.rgb())
            elif self.step % 10 == 0 and not self.step >= self.rpm_alert_min_thres:
                self.image.fill(Color.GREY.rgb())
            else:
                self.image.fill(Color.DARK_GREY.rgb())
