from events import (
    HMI_STARTUP_BACK_BUTTON_PRESSED,
    HMI_STARTUP_BACK_BUTTON_RELEASED,
)
from hmi.views.view import View
from hmi.widgets.button import Button, ButtonState
from hmi.widgets.connection import Connection


class Startup(View):
    def __init__(self, playstation_ip: str):
        super().__init__()

        self.connection_widget = Connection(self.sprite_group, playstation_ip, 650, 86)

        back_button = Button(
            text="x",
            position=(20, 20),
            out_events={
                ButtonState.PRESSED: HMI_STARTUP_BACK_BUTTON_PRESSED,
                ButtonState.RELEASED: HMI_STARTUP_BACK_BUTTON_RELEASED,
            },
        )
        self.button_group.add(back_button)
