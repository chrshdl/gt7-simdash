from hmi.settings import POS
from hmi.properties import Color
from hmi.widget import Widget


class DebugScreen(Widget):
    def __init__(self, groups, w, h, main_fsize=40, header_fsize=32):
        super().__init__(groups, w, h, main_fsize, header_fsize)
        self.rect.topleft = POS["debug"]
        self.car_on_track = True
        self.loading_or_processing = False
        self.paused = False

    def update(self, packet):
        super().update()

        self.car_on_track = packet.flags.car_on_track
        dbg_track = f"on track: {self.car_on_track}"
        dbg = self.header_font.render(dbg_track, False, Color.LIGHT_GREY.rgb())
        midtop = tuple(map(sum, zip(self.image.get_rect().midtop, (0, 10))))
        self.image.blit(dbg, dbg.get_rect(midtop=midtop))

        self.loading_or_processing = packet.flags.loading_or_processing
        dbg_loading = f"loading: {self.loading_or_processing}"
        dbg2 = self.header_font.render(dbg_loading, False, Color.LIGHT_GREY.rgb())
        center = self.image.get_rect().center
        self.image.blit(dbg2, dbg2.get_rect(center=center))

        self.paused = packet.flags.paused
        dbg_paused = f"paused: {self.paused}"
        dbg3 = self.header_font.render(dbg_paused, False, Color.LIGHT_GREY.rgb())
        midbottom = tuple(map(sum, zip(self.image.get_rect().midbottom, (0, -10))))
        self.image.blit(dbg3, dbg3.get_rect(midbottom=midbottom))
