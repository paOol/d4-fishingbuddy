"""Screen capture via mss.

We only ever READ pixels from the screen — no game memory is touched. This is
why exclusive-fullscreen can hand us black frames; the README tells the user to
run D4 in "Windowed Fullscreen" (borderless), which captures cleanly.
"""
from __future__ import annotations

import numpy as np
import mss


class Grabber:
    """Thin wrapper around an mss instance. Reusable; keep one per thread."""

    def __init__(self):
        self._sct = mss.mss()

    @property
    def primary_monitor(self) -> dict:
        # monitors[0] is the union of all screens; monitors[1] is the primary.
        mons = self._sct.monitors
        return mons[1] if len(mons) > 1 else mons[0]

    def grab_bgr(self, box: dict) -> np.ndarray:
        """Grab the given region and return a contiguous BGR uint8 array."""
        shot = self._sct.grab(box)
        # mss gives BGRA; drop alpha, keep BGR (what OpenCV expects).
        frame = np.asarray(shot)[:, :, :3]
        return np.ascontiguousarray(frame)

    def close(self):
        try:
            self._sct.close()
        except Exception:
            pass
