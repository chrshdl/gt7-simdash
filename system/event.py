class Event(object):
    def __init__(self, type, data=None):
        self.type = type
        self.data = data

    @property
    def type(self):
        return self.type

    @property
    def data(self):
        return self.data

