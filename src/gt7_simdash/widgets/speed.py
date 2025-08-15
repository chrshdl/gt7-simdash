from typing import Any

from ..core.utils import FontFamily
from ..widgets.base.colors import Color
from ..widgets.base.label import Label
from ..widgets.base.widget import Anchor, Widget


class SpeedLabel(Widget):
    """Speed indicator that composes a :class:`Label` internally."""

    def __init__(self, anchor: Anchor) -> None:
        """Create the speed label.

        Parameters
        ----------
        anchor : Anchor
            Function mapping ``(width, height)`` → center position for the label.
        """
        self._label = Label(
            text="0",
            font_name=FontFamily.DIGITAL_7_MONO,
            font_size=120,
            color=Color.WHITE.rgb(),
            pos=(0, 0),
            center=True,
        )
        self._anchor = anchor

    def enter(self) -> None:
        """No-op hook for symmetry with :class:`Widget`."""
        pass

    def exit(self) -> None:
        """No-op hook for symmetry with :class:`Widget`."""
        pass

    def handle_event(self, event: Any) -> bool:
        """Passive widget; never consumes events."""
        return False

    def update(self, model: Any, dt: float) -> None:
        """Convert speed from m/s to km/h and update the visible text."""
        speed_kmh = int(((getattr(model, "car_speed", 0.0) or 0.0) * 3.6))
        self._label.set_text(f"{speed_kmh}")

    def draw(self, surface: Any) -> None:
        """Anchor the label and draw it to the surface."""
        w, h = surface.get_size()
        self._label.rect.center = self._anchor((w, h))
        self._label.draw(surface)
