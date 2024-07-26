import time
from hmi.settings import *
from hmi.color import Color
from hmi.widget import Widget


class CurrentLap(Widget):
    def __init__(self, groups, w, h):
        super().__init__(groups, w, h)
        self.rect.center = POS["curr_lap"]

    def update(self, dt, packet=None):
        super().update()

        llt = packet.last_lap_time

        if llt is None:
            llt_str = "--:--"
        else:
            llt_str = time.strftime(
                "%M:%S.{}".format(llt % 1000), time.gmtime(llt / 1000.0)
            )
        llt_render = self.main_font.render(llt_str, False, Color.GREEN.rgb())
        res = tuple(map(sum, zip(self.image.get_rect().midbottom, (0, 0))))
        self.image.blit(llt_render, llt_render.get_rect(midbottom=res))
        label = self.header_font.render("Last Lap", False, Color.WHITE.rgb())
        midtop = tuple(map(sum, zip(self.image.get_rect().midtop, (0, 10))))
        self.image.blit(label, label.get_rect(midtop=midtop))


class BestLap(Widget):
    def __init__(self, groups, w, h):
        super().__init__(groups, w, h)
        self.rect.center = POS["best_lap"]

    def update(self, dt, packet=None):
        super().update()

        blt = packet.best_lap_time

        if blt is None:
            blt_str = "--:--"
        else:
            blt_str = time.strftime(
                "%M:%S.{}".format(blt % 1000), time.gmtime(blt / 1000.0)
            )
        blt_render = self.main_font.render(blt_str, False, Color.GREEN.rgb())
        res = tuple(map(sum, zip(self.image.get_rect().midbottom, (0, 0))))
        self.image.blit(blt_render, blt_render.get_rect(midbottom=res))
        label = self.header_font.render("Best Lap", False, Color.WHITE.rgb())
        midtop = tuple(map(sum, zip(self.image.get_rect().midtop, (0, 10))))
        self.image.blit(label, label.get_rect(midtop=midtop))


class Lap(Widget):
    def __init__(self, groups, w, h, main_fsize=48):
        super().__init__(groups, w, h, main_fsize)
        self.rect.center = POS["lap"]

    def update(self, dt, packet=None):
        super().update()

        curr_lap = packet.lap_count
        total_laps = packet.laps_in_race

        if curr_lap is None and total_laps is None:
            curr_lap = 0
            total_laps = 0

        lap_render = self.main_font.render(
            f"{min(curr_lap, total_laps)} / {total_laps}", False, Color.GREEN.rgb()
        )
        res = tuple(map(sum, zip(self.image.get_rect().midbottom, (0, 0))))
        self.image.blit(lap_render, lap_render.get_rect(midbottom=res))
        label = self.header_font.render("Lap", False, Color.WHITE.rgb())
        midtop = tuple(map(sum, zip(self.image.get_rect().midtop, (0, 10))))
        self.image.blit(label, label.get_rect(midtop=midtop))
