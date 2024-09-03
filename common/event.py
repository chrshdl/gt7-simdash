from typing import Generic, TypeVar

from events import EventType

T = TypeVar("T")


class Event(Generic[T]):
    def __init__(self, type: EventType, data: T):
        self._type = type
        self._data = data

    @property
    def type(self) -> EventType:
        return self._type

    @property
    def data(self) -> T:
        return self._data
