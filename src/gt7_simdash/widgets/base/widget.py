from abc import ABC, abstractmethod
from typing import Any, Callable, Tuple

from granturismo.model.packet import Packet

Anchor = Callable[[Tuple[int, int]], Tuple[int, int]]


class Widget(ABC):
    """Interface every on-screen control implements.

    The interface is intentionally small so widgets can be lightweight and
    composable. All widgets should accept the same *model* (the telemetry
    ``Packet``) in :meth:`update` to remain decoupled from higher-level state.
    """

    def enter(self) -> None:
        """Called when the widget becomes active/visible.

        Use this for lazy allocation (surfaces, fonts, caches) or to start
        animations/timers. Implementations should be fast.
        """
        pass

    def exit(self) -> None:
        """Called when the widget is removed/hidden.

        Use this to release resources or stop timers. Implementations must be
        idempotent; calling multiple times should be safe.
        """
        pass

    def handle_event(self, event: Any) -> bool:
        """Handle a single input event and indicate whether it was *consumed*.

        Parameters
        ----------
        event : Any
            The incoming event object (typically a ``pygame.event.Event``).

        Returns
        -------
        bool
            ``True`` if this widget handled the event and it should **not** be
            propagated to widgets underneath (i.e., the event is *consumed*);
            ``False`` to allow the event to continue bubbling to other widgets.

        Notes
        -----
        - Purely visual widgets (labels, gauges) generally return ``False``.
        - In a :class:`WidgetGroup`, children are queried in **reverse order**
          (top-most first) and propagation stops at the first ``True``.
        - Implementations should be cheap for unrelated event types and avoid
            side effects when returning ``False``.
        """
        return False

    @abstractmethod
    def update(self, model: Packet, dt: float) -> None:
        """Advance internal state for the current frame.

        Parameters
        ----------
        model : Any
            The data model for this frame; in this project it's the telemetry
            ``Packet``. Widgets read any fields they need from it.
        dt : float
            Delta time in seconds since the previous frame (for animations or
            smoothing). Widgets may ignore this if not needed.
        """
        ...

    @abstractmethod
    def draw(self, surface: Any) -> None:
        """Render the widget onto the given surface.

        Parameters
        ----------
        surface : Any
            A ``pygame.Surface`` to draw into. Widgets should not flip the
            display or clear the surface; that is managed by the caller.
        """
        ...
