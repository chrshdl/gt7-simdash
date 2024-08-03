class EventDispatcher:
    events = dict()

    @classmethod
    def has_listener(cls, event, listener):
        if event in cls.events.keys():
            return listener in cls.events[event]
        return False

    @classmethod
    def dispatch(cls, event):
        if event.type in cls.events.keys():
            listeners = cls.events[event.type]
            for listener in listeners:
                listener(event)

    @classmethod
    def add_listener(cls, event, listener):
        if not cls.has_listener(event, listener):
            listeners = cls.events.get(event, [])
            listeners.append(listener)
            cls.events[event] = listeners

