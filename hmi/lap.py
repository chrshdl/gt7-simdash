from datetime import datetime, timezone
from hmi.settings import *
from hmi.color import Color
from hmi.widget import Widget


class CurrentLap(Widget):
    def __init__(self, groups, w, h, main_fsize=40, header_fsize=42):
        super().__init__(groups, w, h, main_fsize, header_fsize)
        self.rect.center = POS["curr_lap_time"]
        self.delta_time = 0
        self.previous_lap = 0
        self.previous_lap_time = 0

    def update(self, dt, packet=None):
        super().update()

        lap_time_str = "--:--"

        if packet.lap_count == 0 or packet.lap_count == None:
            self.delta_time = packet.received_time
        if packet.lap_count != 0 and packet.lap_count == self.previous_lap + 1:
            self.delta_time = packet.received_time
            self.previous_lap = packet.lap_count
            previous_time = datetime.strftime(
                datetime.fromtimestamp(self.previous_lap_time, tz=timezone.utc),
                "%M:%S.%f",
            )[:-3]
            print(f"previous lap time: {previous_time}")
        if (
            packet.laps_in_race != None
            and packet.lap_count != None
            and packet.laps_in_race < packet.lap_count
        ):
            lap_time = self.previous_lap_time
            self.previous_lap = 0
        else:
            lap_time = packet.received_time - self.delta_time
            self.previous_lap_time = lap_time
        lap_time_str = datetime.strftime(
            datetime.fromtimestamp(lap_time, tz=timezone.utc), "%M:%S.%f"
        )[:-3]

        llt_render = self.main_font.render(lap_time_str, False, Color.GREEN.rgb())
        res = tuple(map(sum, zip(self.image.get_rect().midbottom, (0, 0))))
        self.image.blit(llt_render, llt_render.get_rect(midbottom=res))
        label = self.header_font.render("Current Lap", False, Color.WHITE.rgb())
        midtop = tuple(map(sum, zip(self.image.get_rect().midtop, (2, 10))))
        self.image.blit(label, label.get_rect(midtop=midtop))


class BestLap(Widget):
    def __init__(self, groups, w, h, main_fsize=40, header_fsize=42):
        super().__init__(groups, w, h, main_fsize, header_fsize)
        self.rect.center = POS["best_lap_time"]

    def update(self, dt, packet=None):
        super().update()

        blt = packet.best_lap_time

        if blt is None:
            blt_str = "--:--"
        else:
            blt_str = datetime.strftime(
                datetime.fromtimestamp(blt, tz=timezone.utc),
                "%M:%S.%f",
            )[:-3]
        blt_render = self.main_font.render(blt_str, False, Color.GREEN.rgb())
        res = tuple(map(sum, zip(self.image.get_rect().midbottom, (0, 0))))
        self.image.blit(blt_render, blt_render.get_rect(midbottom=res))
        label = self.header_font.render("Best Lap", False, Color.WHITE.rgb())
        midtop = tuple(map(sum, zip(self.image.get_rect().midtop, (0, 10))))
        self.image.blit(label, label.get_rect(midtop=midtop))


class Laps(Widget):
    def __init__(self, groups, w, h, main_fsize=48, header_fsize=42):
        super().__init__(groups, w, h, main_fsize, header_fsize)
        self.rect.center = POS["laps"]

    def update(self, dt, packet=None):
        super().update()

        current = packet.lap_count
        total = packet.laps_in_race

        current = 0 if current is None else current
        total = 0 if total is None else total

        lap_render = self.main_font.render(
            f"{min(current, total)} / {total}", False, Color.GREEN.rgb()
        )
        res = tuple(map(sum, zip(self.image.get_rect().midbottom, (0, 0))))
        self.image.blit(lap_render, lap_render.get_rect(midbottom=res))
        label = self.header_font.render("Lap", False, Color.WHITE.rgb())
        midtop = tuple(map(sum, zip(self.image.get_rect().midtop, (0, 10))))
        self.image.blit(label, label.get_rect(midtop=midtop))
