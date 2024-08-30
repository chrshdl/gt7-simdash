from typing import Any, Optional

from events import EventType


class Event(object):
    def __init__(self, type: EventType, data: Optional[Any] = None):
        self._type = type
        self._data = data

    @property
    def type(self) -> EventType:
        return self._type

    @property
    def data(self) -> Optional[Any]:
        return self._data
