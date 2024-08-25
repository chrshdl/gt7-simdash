import re
import socket

import pygame

from common.logger import Logger
from hmi.widgets.button import Button
from hmi.widgets.textfield import Textfield

# Regex pattern for matching IPv4 addresses
IPV4_PATTERN = r"([0-9]{1,3})\.([0-9]{1,3})\.([0-9]{1,3})\.([0-9]{1,3})"


def get_host_ip_address() -> str:
    return socket.gethostbyname(socket.gethostname())


def get_ip_prefill(host_ip: str) -> str:
    """Returns the standard group of the given IP_v4-address, if it not localhost
    Example:
    get_ip_prefill("192.168.1.4") == "192.168.1."
    get_ip_prefill("127.0.0.1") == ""
    """
    if host_ip == "127.0.0.1":
        return ""
    matches = re.findall(IPV4_PATTERN, host_ip)
    if len(matches) == 0:
        return ""
    first = int(matches[0][0])
    if first <= 127:
        return matches[0][0] + "."
    if first <= 191:
        return matches[0][0] + "." + matches[0][1] + "."
    return matches[0][0] + "." + matches[0][1] + "." + matches[0][2] + "."


class Wizard:
    def __init__(self):
        self.logger = Logger(self.__class__.__name__).get()
        self.screen = pygame.display.get_surface()
        self.wizard = pygame.sprite.Group()

        prefill_ip = get_ip_prefill(get_host_ip_address())
        self.logger.info(f"prefill ip: {prefill_ip}")
        self.tf = Textfield(self.wizard, 360, 80, text=prefill_ip)

        labels = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0", ".", "<", "OK"]
        self.buttons = [
            Button(f"{labels[i]}", (68 * i + 60, 280)) for i in range(len(labels))
        ]

    def handle_events(self, events):
        for button in self.buttons:
            button.render(self.screen)
            if button.is_pressed(events):
                self.tf.append(button.text)

    def update(self, packet):
        self.wizard.update(packet)
        self.wizard.draw(self.screen)
