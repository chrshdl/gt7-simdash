from typing import Any, Iterable, List

from ...widgets.base.widget import Widget


class WidgetGroup(Widget):
    """Composite of widgets that forwards lifecycle, events, update, and draw.

    Children are drawn in insertion order. Events are dispatched in reverse
    order (top-most first) and stop at the first child that returns ``True``.
    """

    def __init__(self, children: Iterable[Widget] | None = None) -> None:
        """Create an empty group or initialize it with children.

        Parameters
        ----------
        children : Iterable[Widget] | None
            Optional sequence of child widgets to add in order.
        """
        self.children: List[Widget] = list(children or [])

    def add(self, w: Widget) -> None:
        """Append a child widget at the end (top-most draw order)."""
        self.children.append(w)

    def extend(self, ws: Iterable[Widget]) -> None:
        """Append multiple child widgets in order."""
        self.children.extend(ws)

    def remove(self, w: Widget) -> None:
        """Remove the first matching child widget.

        Raises
        ------
        ValueError
            If the widget is not a child of this group.
        """
        self.children.remove(w)

    def clear(self) -> None:
        """Remove all children from this group."""
        self.children.clear()

    # lifecycle
    def enter(self) -> None:
        """Propagate :meth:`Widget.enter` to all children in order."""
        for w in self.children:
            w.enter()

    def exit(self) -> None:
        """Propagate :meth:`Widget.exit` to all children in order."""
        for w in self.children:
            w.exit()

    def handle_event(self, event: Any) -> bool:
        """Dispatch an event to children from top-most to bottom-most.

        Returns ``True`` if any child consumed the event.
        """
        for w in reversed(self.children):
            if w.handle_event(event):
                return True
        return False

    def update(self, model: Any, dt: float) -> None:
        """Advance all children one frame using the shared *model* and *dt*."""
        for w in self.children:
            w.update(model, dt)

    def draw(self, surface: Any) -> None:
        """Draw all children in insertion order onto *surface*."""
        for w in self.children:
            w.draw(surface)
