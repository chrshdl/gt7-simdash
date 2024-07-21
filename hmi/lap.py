import time
from hmi.color import Color
from hmi.widget import AbstractWidget


class LastLap(AbstractWidget):
    def update(self, data):
        super().update(data)

        llt = data.last_lap_time

        if llt is None:
            llt_str = "--:--"
        else:
            llt_str = time.strftime(
                "%M:%S.{}".format(llt % 1000), time.gmtime(llt / 1000.0)
            )
        llt_render = self.primary_font.render(llt_str, False, Color.GREEN.rgb())
        res = tuple(map(sum, zip(self.image.get_rect().midbottom, (0, 0))))
        self.image.blit(llt_render, llt_render.get_rect(midbottom=res))
        label = self.recondary_font.render("Last Lap", False, Color.WHITE.rgb())
        midtop = tuple(map(sum, zip(self.image.get_rect().midtop, (0, 10))))
        self.image.blit(label, label.get_rect(midtop=midtop))


class BestLap(AbstractWidget):
    def update(self, data):
        super().update(data)

        blt = data.best_lap_time

        if blt is None:
            blt_str = "--:--"
        else:
            blt_str = time.strftime(
                "%M:%S.{}".format(blt % 1000), time.gmtime(blt / 1000.0)
            )
        blt_render = self.primary_font.render(blt_str, False, Color.GREEN.rgb())
        res = tuple(map(sum, zip(self.image.get_rect().midbottom, (0, 0))))
        self.image.blit(blt_render, blt_render.get_rect(midbottom=res))
        label = self.recondary_font.render("Best Lap", False, Color.WHITE.rgb())
        midtop = tuple(map(sum, zip(self.image.get_rect().midtop, (0, 10))))
        self.image.blit(label, label.get_rect(midtop=midtop))


class Lap(AbstractWidget):
    def update(self, data):
        super().update(data)

        current_lap = data.lap_count
        all_laps = data.laps_in_race

        if current_lap is None and all_laps is None:
            current_lap = 0
            all_laps = 0

        blt_render = self.primary_font.render(
            f"{min(current_lap, all_laps)} / {all_laps}", False, Color.GREEN.rgb()
        )
        res = tuple(map(sum, zip(self.image.get_rect().midbottom, (0, 0))))
        self.image.blit(blt_render, blt_render.get_rect(midbottom=res))
        label = self.recondary_font.render("Lap", False, Color.WHITE.rgb())
        midtop = tuple(map(sum, zip(self.image.get_rect().midtop, (0, 10))))
        self.image.blit(label, label.get_rect(midtop=midtop))
