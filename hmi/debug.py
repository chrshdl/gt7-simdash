from hmi.color import Color
from hmi.widget import AbstractWidget


class DebugScreen(AbstractWidget):
    def update(self, data):
        super().update(data)

        flags = data.flags

        dbg_track = f"on track: {flags.car_on_track}"
        dbg = self.recondary_font.render(dbg_track, False, Color.LIGHT_GREY.rgb())
        midtop = tuple(map(sum, zip(self.image.get_rect().midtop, (0, 10))))
        self.image.blit(dbg, dbg.get_rect(midtop=midtop))

        dbg_loading = f"loading: {flags.loading_or_processing}"
        dbg2 = self.recondary_font.render(dbg_loading, False, Color.LIGHT_GREY.rgb())
        center = self.image.get_rect().center
        self.image.blit(dbg2, dbg2.get_rect(center=center))

        dbg_paused = f"paused: {flags.paused}"
        dbg3 = self.recondary_font.render(dbg_paused, False, Color.LIGHT_GREY.rgb())
        midbottom = tuple(map(sum, zip(self.image.get_rect().midbottom, (0, -10))))
        self.image.blit(dbg3, dbg3.get_rect(midbottom=midbottom))
