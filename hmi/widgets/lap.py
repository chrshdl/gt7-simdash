from datetime import datetime, timezone

from scipy.spatial import KDTree

from common.evendispatcher import EventDispatcher
from common.event import Event
from events import RACE_NEW_LAP_STARTED, RACE_RETRY_STARTED
from hmi.properties import Color, TextAlignment
from hmi.settings import POS

from . import Widget


class EstimatedLap(Widget):
    def __init__(self, groups, w, h, mfs=64, hfs=42):
        super().__init__(groups, w, h, mfs, hfs)
        self.rect.center = POS["est_lap_time"]
        self.header_text = "Lap Time"
        self.body_text_alignment = TextAlignment.MIDBOTTOM
        self.lap = -1
        self.curr_laptime = 0
        self.track_positions = dict()
        self.checkpoints = None
        self.route = None

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
            self.body_text_color = Color.WHITE.rgb()
            self.track_positions.clear()
            EventDispatcher.dispatch(Event(RACE_RETRY_STARTED))
        else:
            if self.lap != current_lap:
                if not race_over:
                    EventDispatcher.dispatch(Event(RACE_NEW_LAP_STARTED, current_lap))
                    self.lap = current_lap
                    self.curr_laptime = 0

            if self.lap != 0:
                self.curr_laptime += 1 / 60 if not paused and not race_over else 0

            estimated_laptime = datetime.strftime(
                datetime.fromtimestamp(self.curr_laptime, tz=timezone.utc), "%M:%S.%f"
            )[:-4]

            if current_lap == 1:
                self.track_positions[(packet.position.x, packet.position.z)] = (
                    self.curr_laptime
                )

            if not race_over and current_lap > 1:
                if self.route is None:
                    self.checkpoints = list(self.track_positions.keys())
                    self.route = KDTree(self.checkpoints)
                _, index = self.route.query((packet.position.x, packet.position.z), k=1)
                prev_checkpoint_time = self.track_positions[self.checkpoints[index]]
                diff = self.curr_laptime - prev_checkpoint_time
                self.body_text_color = (
                    Color.GREEN.rgb() if diff < 0 else Color.RED.rgb()
                )
                estimated_laptime = f"{diff:.2f}"

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
                datetime.fromtimestamp(blt * 1e-3, tz=timezone.utc), "%M:%S.%f"
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
