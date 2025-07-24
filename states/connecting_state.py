import math
import threading
from os.path import join

import pygame
from granturismo.intake.feed import Feed

import states
from common.logger import Logger
from events import (
    BACK_TO_MENU_PRESSED,
    BACK_TO_MENU_RELEASED,
    CONNECTION_FAILED,
    CONNECTION_SUCCESS,
)
from states.state import State
from widgets.button import Button, ButtonGroup
from widgets.properties.colors import Color


class ConnectingState(State):
    def __init__(self, state_manager, ip_address):
        super().__init__()
        self.state_manager = state_manager
        self.ip_address = ip_address
        self.cancel_event = threading.Event()
        self.logger = Logger(__class__.__name__).get()
        self.feed = None
        self.worker = threading.Thread(
            target=self._try_connect_feed_worker,
            daemon=True,
        )

        cancel_button = Button(
            (320, 350, 160, 60),
            "Cancel",
            BACK_TO_MENU_PRESSED,
            BACK_TO_MENU_RELEASED,
        )
        self.button_group = ButtonGroup()
        self.button_group.extend([cancel_button])

        self.start_time = None
        self.error_shown = False
        self.error_time = None
        self.timeout = 10
        self.connection_timeout = 5

    def enter(self):
        super().enter()
        self.start_time = pygame.time.get_ticks() / 1000.0
        self.error_shown = False
        self.error_time = None
        self.cancel_event.clear()

        self.worker.start()

    def _try_connect_feed_worker(self):
        """
        Tries to connect to the PlayStation by sending a heartbeat and listening for telemetry.
        Does NOT instantiate Feed (that must be done in the main thread).
        Posts CONNECTION_SUCCESS or CONNECTION_FAILED as pygame events.
        """
        import platform
        import socket
        import time

        received = False
        sock = None
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            if platform.system() == "Darwin" and hasattr(socket, "SO_REUSEPORT"):
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
            sock.settimeout(1.0)
            try:
                sock.bind(("", Feed._BIND_PORT))
                # Send the heartbeat to PS5 (only needs to be sent once for handshake)
                sock.sendto(
                    Feed._HEARTBEAT_MESSAGE, (self.ip_address, Feed._HEARTBEAT_PORT)
                )
                start = time.time()
                while (
                    not self.cancel_event.is_set()
                    and time.time() - start < self.connection_timeout
                ):
                    try:
                        data, addr = sock.recvfrom(Feed._BUFFER_LEN)
                        if data:
                            received = True
                            break
                    except socket.timeout:
                        self.logger.info("Timeout while connecting, retrying...")
                        continue
            finally:
                if sock:
                    sock.close()
        except Exception as e:
            self.logger.info(f"Socket error in connection worker: {e}")

        if not self.cancel_event.is_set():
            if received:
                self.logger.info("Connection established, posting CONNECTION_SUCCESS.")
                pygame.event.post(pygame.event.Event(CONNECTION_SUCCESS, {}))
            else:
                self.logger.info("Failed to connect, posting CONNECTION_FAILED.")
                pygame.event.post(pygame.event.Event(CONNECTION_FAILED, {}))

    def handle_event(self, event):
        if event.type == CONNECTION_SUCCESS:
            self.on_success(event)
        elif event.type == CONNECTION_FAILED:
            self.on_failed(event)
        elif event.type == BACK_TO_MENU_RELEASED:
            self.on_cancel(event)
        self.button_group.handle_event(event)

    def draw(self, surface):
        surface.fill(Color.BLACK.rgb())
        font = pygame.font.Font(join("assets", "fonts", "pixeltype.ttf"), 68)
        title = font.render("Connecting to Playstation at", False, Color.WHITE.rgb())
        surface.blit(title, (320, 100))

        font = pygame.font.Font(join("assets", "fonts", "digital-7-mono.ttf"), 38)
        text_surface = font.render(f"{self.ip_address}", False, Color.BLUE.rgb())
        text_rect = text_surface.get_rect(center=(surface.get_width() // 2, 180))
        surface.blit(text_surface, text_rect)

        # spinner
        spinner_center = (surface.get_width() // 2, 260)
        self._draw_spinner(surface, spinner_center)

        if self._pending_transition:
            if self.error_shown:
                err_font = pygame.font.Font(
                    join("assets", "fonts", "pixeltype.ttf"), 36
                )
                err_msg = "Could not connect. Please check IP and network."
                err_surface = err_font.render(err_msg, False, Color.LIGHTEST_RED.rgb())
                err_rect = err_surface.get_rect(center=(surface.get_width() // 2, 330))
                surface.blit(err_surface, err_rect)
            else:
                font = pygame.font.Font(join("assets", "fonts", "pixeltype.ttf"), 36)
                msg = "Connected! Launching dashboard..."
                text_surface = font.render(msg, True, (80, 255, 120))
                text_rect = text_surface.get_rect(
                    center=(surface.get_width() // 2, 330)
                )
                surface.blit(text_surface, text_rect)

        self.button_group.draw(surface)

    def on_success(self, event):
        try:
            self.feed = Feed(self.ip_address)
            self.feed.start()
            next_state = states.DashboardState(self.state_manager, self.feed)
            self.request_delayed_transition(next_state, 2.0)
        except Exception as e:
            self.logger.info(f"Failed to create Feed: {e}")
            self.error_shown = True

    def on_failed(self, event):
        self.error_shown = True
        next_state = states.EnterIPState(self.state_manager)
        self.request_delayed_transition(next_state, 3.0)

    def on_cancel(self, event):
        self.cancel_event.set()
        self.state_manager.change_state(states.EnterIPState(self.state_manager))

    def update(self, dt):
        super().update(dt)

        now = pygame.time.get_ticks() / 1000.0
        elapsed = now - self.start_time

        if not self.error_shown and elapsed > self.connection_timeout:
            self.error_shown = True
            self.error_time = now

        if self.error_shown and elapsed > self.timeout:
            self.state_manager.change_state(states.EnterIPState(self.state_manager))

    def exit(self):
        self.cancel_event.set()
        super().exit()

    def _draw_spinner(
        self,
        surface,
        center,
        dot_color=Color.BLUE.rgb(),
        num_dots=3,
        wave_height=18,
        dot_radius=10,
        wave_speed=4,
    ):
        now = pygame.time.get_ticks() / 1000.0
        spacing = 36
        total_width = (num_dots - 1) * spacing
        start_x = center[0] - total_width // 2

        for i in range(num_dots):
            phase = i * 0.22 * math.pi
            y_offset = math.sin(now * wave_speed + phase) * wave_height
            alpha = 160 + int(95 * math.sin(now * wave_speed + phase))
            dot_surf = pygame.Surface((dot_radius * 2, dot_radius * 2), pygame.SRCALPHA)

            pygame.draw.circle(
                dot_surf,
                (*dot_color, alpha),
                (dot_radius, dot_radius),
                dot_radius,
                width=4,
            )
            x = int(start_x + i * spacing)
            y = int(center[1] + y_offset)
            surface.blit(dot_surf, (x - dot_radius, y - dot_radius))
