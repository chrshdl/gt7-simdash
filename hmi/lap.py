from hmi.settings import POS
from hmi.widget import Widget
from datetime import datetime, timezone
import logging

from logformatter import LogFormatter


class EstimatedLap(Widget):
    def __init__(self, groups, w, h, main_fsize=40, header_fsize=42):
        super().__init__(groups, w, h, main_fsize, header_fsize)
        self.rect.center = POS["est_lap_time"]
        self.header_text = "Estimated"

        self.prev_lap = 0
        self.lap = -1
        self.curr_laptime = 0

        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging.DEBUG)

        sh = logging.StreamHandler()
        sh.setLevel(logging.DEBUG)
        sh.setFormatter(LogFormatter())
        self.logger.addHandler(sh)

    def update(self, packet):
        super().update()

        paused = packet.flags.paused
        current_lap = packet.lap_count
        laps_in_race = packet.laps_in_race
        total_laps = packet.lap_count
        self.race_over = (
            laps_in_race < total_laps
            if laps_in_race and total_laps is not None
            else True
        )

        if current_lap == 0:
            estimated_laptime = "--:--"
            self.curr_laptime = 0
            self.prev_lap = 0
        else:
            if self.lap != current_lap:
                if not self.race_over:
                    self.lap = current_lap
                    self.curr_laptime = 0
            if self.lap != 0:
                self.curr_laptime += 1 / 60 if not paused and not self.race_over else 0
            estimated_laptime = datetime.strftime(
                datetime.fromtimestamp(self.curr_laptime, tz=timezone.utc), "%M:%S.%f"
            )[:-3]

        self.body_text = estimated_laptime

    def new_lap_started(self, lap):
        return self.lap != lap


class BestLap(Widget):
    def __init__(self, groups, w, h, main_fsize=40, header_fsize=42):
        super().__init__(groups, w, h, main_fsize, header_fsize)
        self.rect.center = POS["best_lap_time"]
        self.header_text = "Best"

    def update(self, packet):
        super().update()

        blt = packet.best_lap_time

        if blt is None or blt == 0:
            best_lap_time = "--:--"
        else:
            best_lap_time = datetime.strftime(
                datetime.fromtimestamp(blt / 1000, tz=timezone.utc), "%M:%S.%f"
            )[:-3]
        self.body_text = best_lap_time


class Laps(Widget):
    def __init__(self, groups, w, h, main_fsize=48, header_fsize=42):
        super().__init__(groups, w, h, main_fsize, header_fsize)
        self.rect.center = POS["laps"]
        self.header_text = "Laps"

    def update(self, packet):
        super().update()

        current = packet.lap_count
        total = packet.laps_in_race

        current = 0 if current is None else current
        total = 0 if total is None else total

        self.body_text = f"{min(current, total):01d} / {total:01d}"
