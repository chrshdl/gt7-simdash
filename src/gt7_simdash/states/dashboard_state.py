from typing import Optional

from granturismo.intake.feed import Feed, Packet

from ..core.ecu import GearCurveModel
from ..core.events import BACK_TO_MENU_RELEASED
from ..core.logger import Logger
from ..states.state_manager import StateManager
from ..widgets.base.colors import Color
from ..widgets.base.widget_group import WidgetGroup
from ..widgets.button_bar import ButtonBar
from ..widgets.gear import GearLabel
from ..widgets.gear_curves import GearCurvesWidget
from ..widgets.graphical_rpm import GraphicalRPM
from ..widgets.lap import EstimatedLap
from ..widgets.shift_lights import ShiftLights
from ..widgets.speed import SpeedLabel
from .state import State


class DashboardState(State):
    def __init__(
        self,
        state_manager: StateManager,
        feed: Optional[Feed],
    ):
        super().__init__(state_manager)
        self.feed: Optional[Feed] = feed
        self.logger = Logger(__class__.__name__).get()
        self.packet: Optional[Packet] = None
        # Create ECU-side model for learning curves
        self._ecu_model = GearCurveModel()

        shift_lights = ShiftLights(
            anchor=lambda size: (size[0] // 2, size[1] // 16),
            step_thresholds=[0.62, 0.78, 0.92, 0.985],
            color_thresholds=(0.5, 0.8),
            coast_warm_samples=400,
        )
        # la widget tree
        self.widgets = WidgetGroup(
            [
                GraphicalRPM(
                    alert_min=5500,
                    alert_max=9000,
                    max_rpm=9000,
                    redline_rpm=7500,
                ),
                GearLabel(
                    anchor=lambda wh: (wh[0] // 2, wh[1] // 2 + 78),
                ),
                SpeedLabel(anchor=lambda wh: (wh[0] // 2, wh[1] // 5)),
                ButtonBar(
                    on_events={BACK_TO_MENU_RELEASED: self.on_back},
                ),
                EstimatedLap(
                    anchor=lambda size: (size[0] - 150, size[1] // 2 + 160),
                    size=(260, 120),
                    sample_hz=10.0,
                    grid_m=0.25,
                ),
                GearCurvesWidget(
                    anchor=lambda size: (size[0] // 2, size[1] - 100),
                    ecu_model=self._ecu_model,
                    ecu_core=shift_lights._ecu,
                    rpm_max=9000,
                    proxy_max=120.0,
                ),
            ]
        )
        self.widgets.add(shift_lights)

    def enter(self):
        super().enter()
        self.widgets.enter()

    def exit(self):
        try:
            if self.feed is not None:
                self.feed.close()
        except Exception:
            pass
        self.feed = None
        self.widgets.exit()
        super().exit()

    def handle_event(self, event):
        self.widgets.handle_event(event)

    def update(self, dt):
        super().update(dt)
        if not self.feed:
            return
        try:
            pkt: Packet | None = self.feed.get_nowait()
            if pkt:
                self.packet = pkt
        except Exception as e:
            self.logger.info({e})

        if self.packet:
            self.widgets.update(self.packet, dt)

    def draw(self, surface):
        surface.fill(Color.BLACK.rgb())
        self.widgets.draw(surface)

    def on_back(self, event=None):
        from .enter_ip_state import EnterIPState

        self.state_manager.change_state(EnterIPState(self.state_manager))
