import pickle
from . import Widget
from common.evendispatcher import EventDispatcher
from common.event import Event
from hmi.settings import POS
from hmi.properties import TextAlignment
from datetime import datetime, timezone

from events import RACE_NEW_LAP_STARTED, RACE_RETRY_STARTED


class EstimatedLap(Widget):
    def __init__(self, groups, w, h, mfs=64, hfs=42):
        super().__init__(groups, w, h, mfs, hfs)
        self.rect.center = POS["est_lap_time"]
        self.header_text = "Lap Time"
        self.body_text_alignment = TextAlignment.MIDBOTTOM
        self.lap = -1
        self.curr_laptime = 0
        self.laptime_checkpoints = {}

    def update(self, packet):
        super().update()

        paused = packet.flags.paused
        current_lap = packet.lap_count
        total_laps = packet.lap_count

        race_over = (
            total_laps < current_lap if total_laps and total_laps is not None else True
        )

        if current_lap == 0:
            estimated_laptime = "--:--"
            self.curr_laptime = 0
            self.lap = -1
            EventDispatcher.dispatch(Event(RACE_RETRY_STARTED))
        else:
            if self.lap != current_lap:
                if not race_over:
                    EventDispatcher.dispatch(Event(RACE_NEW_LAP_STARTED, current_lap))
                    self.lap = current_lap
                    self.curr_laptime = 0
                    # with open(f"checkpoints-lap-{self.lap}.pickle", "wb") as handle:
                    #    pickle.dump(
                    #        self.laptime_checkpoints,
                    #        handle,
                    #        protocol=pickle.HIGHEST_PROTOCOL,
                    #    )

            if self.lap != 0:
                self.curr_laptime += 1 / 60 if not paused and not race_over else 0
                if self.lap > 0:
                    checkpoints = self.laptime_checkpoints.get(self.lap, [])
                    checkpoints.append((packet.position.x, packet.position.z))
                    self.laptime_checkpoints[self.lap] = checkpoints
            estimated_laptime = datetime.strftime(
                datetime.fromtimestamp(self.curr_laptime, tz=timezone.utc), "%M:%S.%f"
            )[:-4]

        self.body_text = estimated_laptime


class BestLap(Widget):
    def __init__(self, groups, w, h, mfs=64, hfs=42):
        super().__init__(groups, w, h, mfs, hfs)
        self.rect.center = POS["best_lap_time"]
        self.header_text = "Best Time"

    def update(self, packet):
        super().update()

        blt = packet.best_lap_time

        if blt is None or blt == 0:
            best_lap_time = "--:--"
        else:
            best_lap_time = datetime.strftime(
                datetime.fromtimestamp(blt / 1000, tz=timezone.utc), "%M:%S.%f"
            )[:-4]
        self.body_text = best_lap_time


class Laps(Widget):
    def __init__(self, groups, w, h, mfs=64, hfs=42):
        super().__init__(groups, w, h, mfs, hfs)
        self.rect.center = POS["lap"]
        self.header_text = "Lap"

    def update(self, packet):
        super().update()

        current = packet.lap_count
        total = packet.laps_in_race

        current = 0 if current is None else current
        total = 0 if total is None else total

        # self.body_text = f"{min(current, total):01d}/{total:01d}"
        self.body_text = f"{min(current, total):01d}"
