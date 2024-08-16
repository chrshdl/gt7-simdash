import pygame
from hmi.settings import POS
from common.event import Event
from hmi.properties import Color
from hmi.properties import TextAlignment
from . import Widget, EventDispatcher, Logger
from events import HMI_RPM_LEVEL_CHANGED, HMI_CAR_CHANGED


class RPM(Widget):
    LEVEL_0 = 0
    LEVEL_1 = 2
    LEVEL_2 = 4
    LEVEL_3 = 8
    LEVEL_4 = 16

    def __init__(self, groups, w, h, mfs=40, hfs=46):
        super().__init__(groups, w, h, mfs, hfs)

        self._alert_min = self._alert_max = 0
        self.delta = self.RPM_LEVEL_0 = self.RPM_LEVEL_1 = self.RPM_LEVEL_2 = (
            self.RPM_LEVEL_3
        ) = self.RPM_LEVEL_4 = 0

        self._rpm_level = RPM.LEVEL_0
        self.logger = Logger(self.__class__.__name__).get()

        EventDispatcher.add_listener(HMI_CAR_CHANGED, self.on_car_changed)

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


class SimpleRPM(RPM):
    def __init__(self, groups, w, h, mfs=24, hfs=46):
        super().__init__(groups, w, h, mfs, hfs)
        self.rect.center = POS["rpm"]
        self.body_text_alignment = TextAlignment.CENTER

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


class GraphicalRPM(RPM):
    def __init__(self, groups, w, h, mfs=28, hfs=46):
        super().__init__(groups, w, h, mfs, hfs)
        self.w = w
        self.h = h
        self.group = groups
        self.screen_width = pygame.display.get_surface().get_size()[0]
        self.alert_min = 0
        self.alert_max = 0

        self.y = 174
        self.units = []
        self.create_rpm_units(self.alert_min, self.alert_max)
        EventDispatcher.add_listener(HMI_CAR_CHANGED, self.on_car_changed)

    def create_rpm_units(self, alert_min, alert_max):
        if len(self.units) > 0:
            for unit in self.group:
                if isinstance(unit, RPMUnit):
                    self.group.remove(unit)
            self.units.clear()
        for step in range(alert_max + 1):
            self.units.append(
                RPMUnit(
                    self.group,
                    self.screen_width,
                    self.y,
                    alert_min,
                    alert_max,
                    step,
                )
            )

    def on_car_changed(self, event):
        (rpmin, rpmax) = event.data
        self.alert_min = self._normalize(rpmin) - 4
        self.alert_max = self._normalize(rpmax) + 10
        self.create_rpm_units(self.alert_min, self.alert_max)

    def _normalize(self, value):
        return int(value * 0.01)

    def update(self, packet):
        current_rpm = self._normalize(packet.engine_rpm)

        for unit in self.units:
            if unit.step <= current_rpm:
                if current_rpm >= self.alert_min and unit.step >= self.alert_min:
                    unit.image.fill(Color.RED.rgb())
                else:
                    unit.image.fill(Color.GREY.rgb(), (0, 0, self.w, self.h - 2))
            else:
                if unit.step >= self.alert_min:
                    unit.image.fill(Color.DARK_RED.rgb(), (0, 0, self.w, self.h - 2))
                elif unit.step % 10 == 0 and not unit.step >= self.alert_min:
                    unit.image.fill(
                        Color.BLACK.rgb(), (0, 0, self.w, self.h - 2)
                    )  # GREY
                else:
                    unit.image.fill(
                        Color.BLACK.rgb(), (0, 0, self.w, self.h)
                    )  # DARK_GREY


class RPMUnit(pygame.sprite.Sprite):
    def __init__(self, groups, screen_width, y, alert_min, alert_max, name):
        super().__init__(groups)
        w = 2
        h = 35
        margin = 1
        offset_center = (screen_width - alert_max * (margin + w)) // 2
        pos = ((offset_center + (margin + w) * name + margin), y)

        self.step = name

        if name % 10 == 0:
            self.image = pygame.Surface((w, h + 8)).convert()
            if name < alert_min:
                self.image.fill(Color.LIGHT_GREY.rgb())
            else:
                self.image.fill(Color.RED.rgb())
        else:
            self.image = pygame.Surface((w, h)).convert()
        self.rect = self.image.get_rect(topleft=pos)
