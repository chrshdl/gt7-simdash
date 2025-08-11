from ..states.state import State


class StateManager:
    running = False

    def __init__(self, initial_state: State):
        self.current_state: State = initial_state
        self.current_state.enter()

    def handle_event(self, event):
        self.current_state.handle_event(event)

    def update(self, dt):
        self.current_state.update(dt)

    def draw(self, surface):
        self.current_state.draw(surface)

    def change_state(self, new_state):
        self.current_state.exit()
        self.current_state = new_state
        self.current_state.enter()
