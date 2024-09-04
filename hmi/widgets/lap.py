import datetime
import os
import pickle

from scipy.spatial import KDTree

from common.event import Event
from common.eventdispatcher import EventDispatcher
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
        self.estimated_laptime = "--:--"
        self.lap = -1
        self.curr_laptime = 0
        self.prev_laptime = float("inf")
        self.track_positions = dict()
        self.checkpoint_positions = None
        self.checkpoints = None
        self.route = None
        self.is_new_best_lap = False

    def update(self, packet):
        super().update()

        paused = packet.flags.paused
        loading_or_processing = packet.flags.loading_or_processing
        current_lap = packet.lap_count

        if loading_or_processing:
            self.reset()
            EventDispatcher.dispatch(Event(RACE_RETRY_STARTED))

        if current_lap == 0 or current_lap is None:
            self.reset()
        else:
            if self.lap != current_lap:
                laptime = str(
                    datetime.timedelta(
                        seconds=len(self.track_positions.keys()) * 1 / 60
                    )
                )
                print(f"laptime: {laptime}")
                EventDispatcher.dispatch(Event(RACE_NEW_LAP_STARTED, current_lap))
                if current_lap > 1:
                    if self.curr_laptime < self.prev_laptime:
                        self.is_new_best_lap = True
                        self.prev_laptime = self.curr_laptime
                        self.checkpoint_positions = self.track_positions.copy()
                self.curr_laptime = 0
                self.lap = current_lap
                self.save_track("KyotoYamagiwaMiyabi", current_lap - 1)
                self.track_positions.clear()

            if self.lap != 0:
                self.curr_laptime += 1 / 60 if not paused else 0

            self.estimated_laptime = datetime.datetime.strftime(
                datetime.datetime.fromtimestamp(
                    self.curr_laptime, tz=datetime.timezone.utc
                ),
                "%M:%S.%f",
            )[:-4]

            self.track_positions[(packet.position.x, packet.position.z)] = (
                self.curr_laptime
            )

            if current_lap > 1:
                if self.checkpoint_positions:
                    if self.is_new_best_lap:
                        self.is_new_best_lap = False
                    self.checkpoints = list(self.checkpoint_positions.keys())
                    self.route = KDTree(self.checkpoints)
                    _, i = self.route.query((packet.position.x, packet.position.z), k=1)
                    checkpoint_laptime = self.checkpoint_positions[self.checkpoints[i]]
                    diff = self.curr_laptime - checkpoint_laptime
                    self.body_text_color = (
                        Color.GREEN.rgb() if diff < 0 else Color.RED.rgb()
                    )
                    self.estimated_laptime = f"{diff:.1f}"

        self.body_text = self.estimated_laptime

    def save_track(self, name, lap):
        with open(
            os.path.join(
                "notebooks",
                f"{name}-lap-{lap}.pickle",
            ),
            "wb",
        ) as fid:
            pickle.dump(
                self.track_positions,
                fid,
                protocol=pickle.HIGHEST_PROTOCOL,
            )

    def reset(self):
        self.estimated_laptime = "--:--"
        self.curr_laptime = 0
        self.prev_laptime = float("inf")
        self.lap = -1
        self.body_text_color = Color.WHITE.rgb()
        self.track_positions.clear()
        self.route = None
        self.checkpoint_positions = None
        self.is_new_best_lap = False


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
            best_lap_time = datetime.datetime.strftime(
                datetime.datetime.fromtimestamp(blt * 1e-3, tz=datetime.timezone.utc),
                "%M:%S.%f",
            )[:-4]
        self.body_text = best_lap_time


class Laps(Widget):
    def __init__(self, groups, w, h, mfs=64, hfs=42): #mfs = 64, hfs = 42
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
        self.body_text = f"{current:01d}" if not total else f"{min(current, total):01d}"
