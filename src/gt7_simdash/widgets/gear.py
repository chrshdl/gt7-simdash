from typing import Any

from ..core.utils import FontFamily, load_font
from ..widgets.base.colors import Color
from ..widgets.base.label import Label
from ..widgets.base.widget import Anchor, Widget


class GearLabel(Widget):
    """Gear indicator implemented via composition: owns a Label internally."""

    def __init__(self, anchor: Anchor) -> None:
        self._label = Label(
            text="0",
            font=load_font(size=300, dir="digital", name=FontFamily.DIGITAL_7_MONO),
            color=Color.BLUE.rgb(),
            pos=(0, 0),
            center=True,
        )
        # self._label = Label(
        #     text="N   P   1   2  3  4",
        #     font=load_font(size=134, dir="d-din", name=FontFamily.D_DIN_EXP),
        #     color=Color.WHITE.rgb(),
        #     pos=(320, 100),
        #     center=False,
        # )
        self._anchor = anchor

    def enter(self) -> None:
        pass

    def exit(self) -> None:
        pass

    def handle_event(self, event: Any) -> bool:
        return False

    def update(self, model: Any, dt: float) -> None:
        gear = int(getattr(model, "current_gear", 0) or 0)
        self._label.set_text("R" if gear == 0 else str(gear))

    def draw(self, surface: Any) -> None:
        w, h = surface.get_size()
        self._label.rect.center = self._anchor((w, h))
        self._label.draw(surface)
