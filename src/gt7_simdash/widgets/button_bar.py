from typing import Any, Callable, Dict

from ..core.events import BACK_TO_MENU_PRESSED, BACK_TO_MENU_RELEASED
from .base.button import Button, ButtonGroup
from .base.widget import Widget


class ButtonBar(Widget):
    """This widget is a navigation bar with button(s).

    It **implements** :class:`Widget` and **owns** an internal
    :class:`ButtonGroup` with a :class:`Button`. It forwards events and draws
    via the composed group while exposing a clean widget interface.
    """

    def __init__(
        self,
        rect=(40, 540, 100, 50),
        on_events: Dict[int, Callable[[Any], None]] | None = None,
    ) -> None:
        """Create the back button bar.

        Parameters
        ----------
        rect : tuple[int, int, int, int]
            Button rectangle (x, y, w, h).
        text : str
            Caption displayed on the button.
        callbacks : dict[int, Callable]
            Optional event-type -> callback mapping to invoke on release/press.
        event_type_pressed : int | None
            Event type to post when pressed (from your events module).
        event_type_released : int | None
            Event type to post when released.
        """
        self._on_events = on_events or {}
        self._group = ButtonGroup()
        self._group.extend(
            [
                Button(
                    rect=rect,
                    text="Back",
                    event_type_pressed=BACK_TO_MENU_PRESSED,
                    event_type_released=BACK_TO_MENU_RELEASED,
                )
            ]
        )

    def enter(self) -> None:
        """Nothing to allocate beyond what's in __init__."""
        pass

    def exit(self) -> None:
        """Composed widgets are garbage collected by the owner."""
        pass

    def handle_event(self, event: Any) -> bool:
        """Forward event to the internal :class:`ButtonGroup`.

        Returns ``True`` if a registered callback was invoked for this event
        (i.e., the event is considered consumed by this control).
        """
        self._group.handle_event(event)
        callback = self._on_events.get(getattr(event, "type", None))
        if callback:
            callback(event)
            return True
        return False

    def update(self, model: Any, dt: float) -> None:
        """No-op; the button is purely event-driven."""
        pass

    def draw(self, surface: Any) -> None:
        """Delegate rendering to the internal :class:`ButtonGroup`."""
        self._group.draw(surface)
