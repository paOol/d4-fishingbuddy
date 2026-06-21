"""Config loading/saving and ROI geometry.

The config is a plain JSON file so the user can edit it by hand. We strip any
"comment" keys before use so they can document fields inline.
"""
from __future__ import annotations

import json
import os

CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config.json")


def load(path: str = CONFIG_PATH) -> dict:
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def save(cfg: dict, path: str = CONFIG_PATH) -> None:
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(cfg, fh, indent=2)


def roi_box(cfg: dict, monitor: dict) -> dict:
    """Compute the absolute ROI rectangle (mss-style dict) from config + monitor.

    monitor is an mss monitor dict: {left, top, width, height}.
    The ROI is centered on the monitor, then shifted by (offset_x, offset_y),
    and clamped to stay on-screen.
    """
    r = cfg["roi"]
    w, h = int(r["width"]), int(r["height"])
    cx = monitor["left"] + monitor["width"] // 2 + int(r["offset_x"])
    cy = monitor["top"] + monitor["height"] // 2 + int(r["offset_y"])
    left = cx - w // 2
    top = cy - h // 2

    # Clamp to monitor bounds.
    left = max(monitor["left"], min(left, monitor["left"] + monitor["width"] - w))
    top = max(monitor["top"], min(top, monitor["top"] + monitor["height"] - h))
    return {"left": int(left), "top": int(top), "width": w, "height": h}
