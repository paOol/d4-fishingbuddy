"""User feedback: console status line + audible beeps.

Beeps matter because when D4 runs fullscreen the user can't see the console, so
distinct tones tell them what's happening without alt-tabbing.
"""
from __future__ import annotations

import sys

try:
    import winsound  # Windows only

    def _beep(freq: int, ms: int) -> None:
        try:
            winsound.Beep(freq, ms)
        except Exception:
            pass
except ImportError:  # non-Windows (dev box) — no-op so imports still work
    def _beep(freq: int, ms: int) -> None:
        pass


# Named tones for each event.
def beep_on() -> None:      _beep(880, 120); _beep(1175, 120)   # rising = armed
def beep_off() -> None:     _beep(1175, 120); _beep(660, 160)   # falling = idle
def beep_cast() -> None:    _beep(523, 70)
def beep_hook() -> None:    _beep(1568, 90); _beep(2093, 110)   # bright = fish on
def beep_capture() -> None: _beep(2093, 60); _beep(2093, 60)


_COLORS = {"green": "92", "red": "91", "yellow": "93", "cyan": "96", "grey": "90"}


def status(msg: str, color: str = "cyan") -> None:
    code = _COLORS.get(color, "96")
    sys.stdout.write(f"\x1b[{code}m{msg}\x1b[0m\n")
    sys.stdout.flush()
