class Event(object):
    def __init__(self, type, data=None):
        self._type = type
        self._data = data

    @property
    def type(self):
        return self._type

    @property
    def data(self):
        return self._data

