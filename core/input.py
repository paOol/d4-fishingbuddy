"""Keyboard input: sending keys into the game + listening for global hotkeys.

Sending: pydirectinput issues SendInput scancode events, which DirectX games
(D4) accept even when many higher-level APIs are ignored. We never inject into
the game process — these are OS-level synthetic key presses, the same kind a
macro keyboard produces.

Listening: the `keyboard` library installs a low-level hook so our toggle/quit
hotkeys work while D4 has focus.
"""
from __future__ import annotations

import random
import time

import pydirectinput
import keyboard

# We manage our own timing/jitter; disable the library's built-in pause and the
# mouse-corner failsafe (irrelevant for keys, and it would raise mid-run).
pydirectinput.PAUSE = 0.0
pydirectinput.FAILSAFE = False


def tap(key: str, hold: float = 0.05, jitter: float = 0.0) -> None:
    """Press and release a key with a short, optionally randomized hold."""
    h = hold + (random.uniform(0, jitter) if jitter else 0.0)
    pydirectinput.keyDown(key)
    time.sleep(h)
    pydirectinput.keyUp(key)


# Re-export keyboard helpers so callers don't import the lib directly.
add_hotkey = keyboard.add_hotkey
wait = keyboard.wait
