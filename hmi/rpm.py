import pygame
from hmi.color import Color


class RPM(pygame.sprite.Sprite):
    def __init__(self, screen_width, y, rpm_min, rpm_max, step):
        super().__init__()

        self.rpm_min = rpm_min
        self.rpm_max = rpm_max
        margin = 2
        self.w = 4
        self.h = 33

        offset_center = (screen_width - rpm_max * (margin + self.w)) // 2
        pos = ((offset_center + (margin + self.w) * step + margin), y)

        self.step = step

        if self.step % 10 == 0:
            self.image = pygame.Surface((self.w, self.h + 6)).convert()
            if self.step < rpm_min:
                self.image.fill(Color.LIGHT_GREY.rgb())
            else:
                self.image.fill(Color.RED.rgb())
        else:
            self.image = pygame.Surface((self.w, self.h)).convert()

        self.rect = self.image.get_rect(topleft=pos)

    def update(self, current_rpm):
        if self.step <= current_rpm:
            if current_rpm >= self.rpm_min and self.step >= self.rpm_min:
                self.image.fill(Color.RED.rgb())
            else:
                self.image.fill(Color.GREY.rgb(), (0, 0, self.w, self.h))
        else:
            if self.step >= self.rpm_min:
                self.image.fill(Color.DARK_RED.rgb(), (0, 0, self.w, self.h))
            elif self.step % 10 == 0 and not self.step >= self.rpm_min:
                self.image.fill(Color.BLACK.rgb(), (0, 0, self.w, self.h))  # GREY
            else:
                self.image.fill(Color.BLACK.rgb(), (0, 0, self.w, self.h))  # DARK_GREY
