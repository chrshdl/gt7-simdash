from common.event import Event
from common.eventdispatcher import EventDispatcher
from events import HMI_VIEW_BACK, HMI_VIEW_BUTTON_RELEASED
from hmi.views.view import View
from hmi.widgets.button import Button
from hmi.widgets.connection import Connection


class Startup(View):
    def __init__(self, playstation_ip: str):
        super().__init__()

        Connection(self.sprite_group, playstation_ip, 650, 86)

        EventDispatcher.add_listener(HMI_VIEW_BUTTON_RELEASED, self.on_button_released)

        back = Button(text="X", position=(20, 20))
        self.buttons.append(back)

    def on_button_released(self, event):
        if event.data == "X":
            EventDispatcher.dispatch(Event(type=HMI_VIEW_BACK, data=None))