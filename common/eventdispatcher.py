from collections.abc import Callable
from typing import Any

from events import EventType

from .event import Event

Listener = Callable[[Event], Any]


class EventDispatcher:
    events: dict[EventType, list[Listener]] = dict()

    @classmethod
    def has_listener(cls, event_type: EventType, listener: Listener) -> bool:
        if event_type in cls.events.keys():
            return listener in cls.events[event_type]
        return False

    @classmethod
    def dispatch(cls, event: Event) -> None:
        for listener in cls.events.get(event.type, tuple()):
            listener(event)

    @classmethod
    def add_listener(cls, event_type: EventType, listener: Listener) -> None:
        if not cls.has_listener(event_type, listener):
            listeners = cls.events.get(event_type, [])
            listeners.append(listener)
            cls.events[event_type] = listeners
