"""Calibrate the scan region (ROI) so the fishing icon lands inside it.

Run this with D4 in Windowed-Fullscreen on a second monitor, or windowed, so you
can see both the game and this preview. A live, downscaled view of your screen is
shown with the ROI drawn as a green box centered above screen-center.

Controls (focus the 'FishingBuddy ROI' window):
    Arrow keys      move the box (hold Shift-equivalent: press repeatedly)
    + / -           grow / shrink the box
    [ / ]           narrower / wider
    ' / ;           shorter / taller
    s               SAVE offsets+size to config.json
    q  or  Esc      quit without saving

Tip: cast a line in-game, and when the icon appears confirm it's inside the box.
"""
from __future__ import annotations

import cv2
import numpy as np

from core import config
from core.screen import Grabber

STEP = 10
PREVIEW_W = 1100  # downscaled preview width


def main():
    cfg = config.load()
    grab = Grabber()
    mon = grab.primary_monitor
    r = cfg["roi"]

    win = "FishingBuddy ROI"
    cv2.namedWindow(win, cv2.WINDOW_NORMAL)
    scale = PREVIEW_W / mon["width"]

    print("Adjust the green box over the icon area, then press 's' to save.")
    while True:
        full = grab.grab_bgr(mon)
        box = config.roi_box(cfg, mon)

        # Draw ROI rectangle in full-screen coords, then downscale for display.
        x = box["left"] - mon["left"]
        y = box["top"] - mon["top"]
        cv2.rectangle(full, (x, y), (x + box["width"], y + box["height"]),
                      (0, 255, 0), 3)
        # Crosshair at screen center for reference.
        cx, cy = mon["width"] // 2, mon["height"] // 2
        cv2.drawMarker(full, (cx, cy), (0, 0, 255), cv2.MARKER_CROSS, 40, 2)

        preview = cv2.resize(full, (PREVIEW_W, int(mon["height"] * scale)))
        label = (f"off=({r['offset_x']},{r['offset_y']})  "
                 f"size={r['width']}x{r['height']}  "
                 f"[arrows move | +/- size | s save | q quit]")
        cv2.putText(preview, label, (10, 24), cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                    (0, 255, 255), 2)
        cv2.imshow(win, preview)

        # waitKeyEx (not waitKey) so extended arrow-key codes come through intact.
        k = cv2.waitKeyEx(20)
        if k == -1:
            continue
        if k in (ord("q"), 27):
            break
        elif k == ord("s"):
            config.save(cfg)
            print(f"Saved: offset=({r['offset_x']},{r['offset_y']}) "
                  f"size={r['width']}x{r['height']}")
        # Arrow keys (Windows OpenCV codes); fall back to WASD too.
        elif k in (2490368, ord("w")): r["offset_y"] -= STEP   # up
        elif k in (2621440, ord("x")): r["offset_y"] += STEP   # down
        elif k in (2424832, ord("a")): r["offset_x"] -= STEP   # left
        elif k in (2555904, ord("d")): r["offset_x"] += STEP   # right
        elif k == ord("+") or k == ord("="):
            r["width"] += STEP; r["height"] += STEP
        elif k == ord("-") or k == ord("_"):
            r["width"] = max(40, r["width"] - STEP)
            r["height"] = max(40, r["height"] - STEP)
        elif k == ord("]"): r["width"] += STEP
        elif k == ord("["): r["width"] = max(40, r["width"] - STEP)
        elif k == ord("'"): r["height"] = max(40, r["height"] - STEP)
        elif k == ord(";"): r["height"] += STEP

    cv2.destroyAllWindows()
    grab.close()


if __name__ == "__main__":
    main()
