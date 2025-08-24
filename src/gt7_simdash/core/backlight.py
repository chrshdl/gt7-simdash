import glob
import os
from typing import Optional, Tuple


class Backlight:
    """
    Wrapper for Linux backlight sysfs.
    Looks for /sys/class/backlight/*/brightness and max_brightness.
    """

    def __init__(self):
        self._brightness_path: Optional[str] = None
        self._max_path: Optional[str] = None
        self._detect_paths()

    def _detect_paths(self):
        candidates = glob.glob("/sys/class/backlight/*/brightness")
        if candidates:
            self._brightness_path = candidates[0]
            self._max_path = os.path.join(
                os.path.dirname(self._brightness_path), "max_brightness"
            )

    def available(self) -> bool:
        return self._brightness_path is not None and os.path.exists(
            self._brightness_path
        )

    def _read_int(self, path: str) -> Optional[int]:
        try:
            with open(path, "r") as f:
                return int(f.read().strip())
        except Exception:
            return None

    def get_raw(self) -> Optional[Tuple[int, int]]:
        if not self.available():
            return None
        cur = self._read_int(self._brightness_path)
        maxv = self._read_int(self._max_path) if self._max_path else None
        if cur is None or maxv is None or maxv <= 0:
            return None
        return cur, maxv

    def get_percent(self) -> Optional[int]:
        raw = self.get_raw()
        if not raw:
            return None
        cur, maxv = raw
        return int(round((cur / maxv) * 100.0))

    def set_percent(self, percent: float) -> bool:
        """Between 0..100, returns True on success."""
        if not self.available():
            return False
        raw = self.get_raw()
        if not raw:
            return False
        _, maxv = raw
        p = max(0, min(100, int(round(percent))))
        value = int(round((p / 100.0) * maxv))
        try:
            with open(self._brightness_path, "w") as f:
                f.write(str(value))
            return True
        except Exception:
            return False
