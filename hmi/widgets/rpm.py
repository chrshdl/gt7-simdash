from hmi.settings import POS
from system.event import Event
from hmi.properties import TextAlignment
from . import Widget, EventDispatcher, Logger
from events import HMI_RPM_LEVEL_CHANGED, HMI_CAR_CHANGED


class RPM(Widget):

    LEVEL_0 = 0
    LEVEL_1 = 2
    LEVEL_2 = 4
    LEVEL_3 = 8
    LEVEL_4 = 16

    def __init__(self, groups, w, h, mfs=28, hfs=46):
        super().__init__(groups, w, h, mfs, hfs)
        self.rect.center = POS["rpm"]
        self.body_text_alignment = TextAlignment.CENTER

        self._alert_min = self._alert_max = 0
        self.delta = self.RPM_LEVEL_0 = self.RPM_LEVEL_1 = self.RPM_LEVEL_2 = (
            self.RPM_LEVEL_3
        ) = self.RPM_LEVEL_4 = 0

        self._rpm_level = RPM.LEVEL_0

        self.logger = Logger(self.__class__.__name__).get()
        EventDispatcher.add_listener(HMI_CAR_CHANGED, self.on_car_changed)

    def update(self, packet):
        super().update()

        limiter_active = packet.flags.rev_limiter_alert_active
        curr_rpm = int(packet.engine_rpm)
        self.body_text = f"{curr_rpm}"

        self.update_leds(curr_rpm)

    def update_leds(self, curr_rpm):
        if curr_rpm < self.RPM_LEVEL_0:
            if bool(self._rpm_level | RPM.LEVEL_0):
                self.rpm_level(0)
        elif curr_rpm in range(self.RPM_LEVEL_0, self.RPM_LEVEL_1):
            if not bool(self._rpm_level & RPM.LEVEL_1):
                self.rpm_level(2)
        elif curr_rpm in range(self.RPM_LEVEL_1, self.RPM_LEVEL_2):
            if not bool(self._rpm_level & RPM.LEVEL_2):
                self.rpm_level(4)
        elif curr_rpm in range(self.RPM_LEVEL_2, self.RPM_LEVEL_3):
            if not bool(self._rpm_level & RPM.LEVEL_3):
                self.rpm_level(6)
        elif curr_rpm in range(self.RPM_LEVEL_3, self.RPM_LEVEL_4):
            if not bool(self._rpm_level & RPM.LEVEL_4):
                self.rpm_level(8)

    def rpm_level(self, level):
        if self._rpm_level != level:
            self._rpm_level = level
            EventDispatcher.dispatch(Event(HMI_RPM_LEVEL_CHANGED, self._rpm_level))

    @property
    def alert_min(self):
        return self._alert_min

    @alert_min.setter
    def alert_min(self, value):
        self._alert_min = value

    @property
    def alert_max(self):
        return self._alert_max

    @alert_max.setter
    def alert_max(self, value):
        self._alert_max = value

    def on_car_changed(self, event):
        (rpmin, rpmax) = event.data
        self.logger.info(f"New RPM alert values:({rpmin}, {rpmax})")
        self._alert_min = rpmin
        self._alert_max = rpmax
        self.update_rpm_alerts()

    def update_rpm_alerts(self):
        self.delta = int((self._alert_max - self._alert_min) * 2)
        self.RPM_LEVEL_0 = int(self._alert_min - 2 * self.delta)
        self.RPM_LEVEL_1 = int(self._alert_min - 1.5 * self.delta)
        self.RPM_LEVEL_2 = int(self._alert_min - self.delta)
        self.RPM_LEVEL_3 = int(self._alert_min - 0.5 * self.delta)
        self.RPM_LEVEL_4 = int(self._alert_max)
        self.logger.info(
            f"New RPM levels: {self.RPM_LEVEL_0} | {self.RPM_LEVEL_1} | {self.RPM_LEVEL_2} | {self.RPM_LEVEL_3} | {self.RPM_LEVEL_4}"
        )
        self.logger.info(f"New RPM delta: {self.delta}")

