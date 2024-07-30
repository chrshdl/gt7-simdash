from hmi.settings import POS
from hmi.widget import Widget
from datetime import datetime, timezone
import logging

from logformatter import LogFormatter


class CurrentLap(Widget):
    def __init__(self, groups, w, h, main_fsize=40, header_fsize=42):
        super().__init__(groups, w, h, main_fsize, header_fsize)
        self.rect.center = POS["curr_lap_time"]
        self.header = "Current Lap"
        self.delta_time = 0
        self.previous_lap = 0
        self.previous_lap_time = 0

        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging.DEBUG)

        sh = logging.StreamHandler()
        sh.setLevel(logging.DEBUG)
        sh.setFormatter(LogFormatter())
        self.logger.addHandler(sh)

    def update(self, packet):
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
            self.logger.debug(f"PREVIOUS LAP TIME WAS: {previous_time}")
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

        self.value = lap_time_str


class BestLap(Widget):
    def __init__(self, groups, w, h, main_fsize=40, header_fsize=42):
        super().__init__(groups, w, h, main_fsize, header_fsize)
        self.rect.center = POS["best_lap_time"]
        self.header = "Best Lap"

    def update(self, packet):
        super().update()

        blt = packet.best_lap_time

        if blt is None or blt == 0:
            best_lap_time = "--:--"
        else:
            best_lap_time = datetime.strftime(
                datetime.fromtimestamp(blt / 1000, tz=timezone.utc), "%M:%S.%f"
            )[:-3]
        self.value = best_lap_time


class Laps(Widget):
    def __init__(self, groups, w, h, main_fsize=48, header_fsize=42):
        super().__init__(groups, w, h, main_fsize, header_fsize)
        self.rect.center = POS["laps"]
        self.header = "Laps"

    def update(self, packet):
        super().update()

        current = packet.lap_count
        total = packet.laps_in_race

        current = 0 if current is None else current
        total = 0 if total is None else total

        self.value = f"{min(current, total)} / {total}"
