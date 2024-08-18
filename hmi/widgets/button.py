import pygame
from os.path import join
from hmi.properties import Color


class Button:
    def __init__(
        self, text, position, size=(60, 50), fs=50, outline=True, gradient=False
    ):
        self.text = text
        self.position = position
        self.size = size
        self.button = pygame.Surface(size).convert()
        self.button.fill(Color.DARK_GREY.rgb())
        self.outline = outline
        self.gradient = gradient
        self.top = pygame.Color(0, 0, 0)
        self.gradient_outline_color = Color.GREY.rgb()

        font = pygame.font.Font(join("fonts", "pixeltype.ttf"), fs)

        self.text_surf = font.render(f"{text}", False, (255, 255, 255))

    def update(self, packet):
        if self.text == "TCS":
            if packet.flags.tcs_active:
                self.gradient = True
                self.top = pygame.Color(Color.DARK_GREEN.rgb())
                self.gradient_outline_color = Color.GREEN.rgb()
            if not packet.flags.tcs_active:
                self.gradient = False
        if self.text == "BEAM":
            if packet.flags.lights_high_beams_active:
                self.gradient = True
                self.top = pygame.Color(0, 50, 124)
                self.gradient_outline_color = Color.BLUE.rgb()
            if not packet.flags.lights_high_beams_active:
                self.gradient = False

    def is_pressed(self, events):
        mousePos = pygame.mouse.get_pos()
        if self.is_within_button_area(
            mousePos[0],
            mousePos[1],
            self.size[0],
            self.size[1],
            self.position[0],
            self.position[1],
        ):
            for event in events:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.gradient = True
                    self.top = Color.DARK_BLUE.rgb()
                    self.gradient_outline_color = Color.BLUE.rgb()
                    return True
                if event.type == pygame.MOUSEBUTTONUP:
                    self.gradient = False
        return False

    def render(self, display):
        if self.gradient:
            self.draw_gradient(
                top=self.top,
                bottom=Color.DARKEST_BLUE.rgb(),
            )
        if not self.gradient:
            pygame.draw.rect(
                self.button, Color.BLACK.rgb(), self.button.get_rect(), 0, 1
            )
        textx = (
            self.position[0]
            + (self.button.get_rect().width / 2)
            - (self.text_surf.get_rect().width / 2)
        )
        texty = (
            self.position[1]
            + (self.button.get_rect().height / 2)
            - (self.text_surf.get_rect().height / 2 - 3)
        )

        display.blit(self.button, (self.position[0], self.position[1]))
        display.blit(self.text_surf, (textx, texty))

        if self.outline:
            thickness = 2
            posx = self.position[0] - thickness
            posy = self.position[1] - thickness
            sizex = self.size[0] + thickness * 2
            sizey = self.size[1] + thickness * 2

            if self.gradient:
                color = self.gradient_outline_color
            else:
                color = Color.DARK_GREY.rgb()

            pygame.draw.rect(
                display,
                color,
                (posx, posy, sizex, sizey),
                thickness,
                4,
            )

    def is_within_button_area(self, px, py, rw, rh, rx, ry):
        if px > rx and px < rx + rw:
            if py > ry and py < ry + rh:
                return True
        return False

    def draw_gradient(self, top, bottom):
        w = self.button.get_rect().width
        h = self.button.get_rect().height
        for y in range(0, h, 1):
            color = pygame.Color(top).lerp(pygame.Color(bottom), y / h)
            self.button.fill(color, (0, y, w, 1))
