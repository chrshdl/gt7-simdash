from typing import Any

from granturismo.model.packet import Packet

from ..core.utils import FontFamily, load_font
from ..widgets.base.colors import Color
from ..widgets.base.label import Label
from ..widgets.base.widget import Anchor, Widget


class SpeedLabel(Widget):
    """Speed indicator"""

    def __init__(self, anchor: Anchor) -> None:
        """Create the speed label

        Parameters
        anchor : Anchor
            Function mapping ``(width, height)`` -> center position for the label.
        """
        self._label = Label(
            text="0",
            font=load_font(size=120, dir="digital", name=FontFamily.DIGITAL_7_MONO),
            color=Color.WHITE.rgb(),
            pos=(0, 0),
            center=True,
        )
        self._anchor = anchor

    def enter(self) -> None:
        pass

    def exit(self) -> None:
        pass

    def handle_event(self, event: Any) -> bool:
        """Never consumes events"""
        return False

    def update(self, model: Packet, dt: float | None = None) -> None:
        speed_kmh = int(((getattr(model, "car_speed", 0.0) or 0.0) * 3.6))
        self._label.set_text(f"{speed_kmh}")

    def draw(self, surface: Any) -> None:
        w, h = surface.get_size()
        self._label.rect.center = self._anchor((w, h))
        self._label.draw(surface)
