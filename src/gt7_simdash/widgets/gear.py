from typing import Any

from ..core.utils import FontFamily
from ..widgets.base.colors import Color
from ..widgets.base.label import Label
from ..widgets.base.widget import Anchor, Widget


class GearLabel(Widget):
    """Gear indicator implemented via composition: owns a Label internally."""

    def __init__(self, anchor: Anchor) -> None:
        self._label = Label(
            text="0",
            font_name=FontFamily.DIGITAL_7_MONO,
            font_size=240,
            color=Color.BLUE.rgb(),
            pos=(0, 0),
            center=True,
        )
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
