class Container:
    """Simple container that forwards draw/handle_event to children when visible."""

    def __init__(self, is_visible: bool = True):
        self.is_visible = is_visible
        self._children = []

    def add(self, *widgets):
        self._children.extend(widgets)

    def draw(self, surface):
        if not self.is_visible:
            return
        for w in self._children:
            if hasattr(w, "draw"):
                w.draw(surface)

    def handle_event(self, event):
        if not self.is_visible:
            return
        for w in self._children:
            if hasattr(w, "handle_event"):
                w.handle_event(event)
