"""Capture the fishing-icon template used for detection.

Because the icon only shows for ~1 second, you grab it live with a global hotkey
while playing normally:

    1. Run this script (as Administrator if D4 is elevated).
    2. Alt-tab back into D4 and cast a line (F1).
    3. The instant the fishing icon appears over your head, press F7.
       Two quick beeps = template saved to icon_template.png.
    4. Repeat a couple times to get a clean grab; the latest one wins. Each grab
       is also archived as templates/icon_YYYY... so you can pick the best.

The template is just the current ROI crop, so calibrate_roi.py FIRST (tight box
around where the icon appears => cleaner matches).
"""
from __future__ import annotations

import os
import threading
import time

import cv2

from core import config, feedback
from core.screen import Grabber
from core.input import add_hotkey

ARCHIVE_DIR = os.path.join(os.path.dirname(__file__), "templates")


def main():
    cfg = config.load()
    grab = Grabber()
    box = config.roi_box(cfg, grab.primary_monitor)
    out_path = cfg["detection"]["template_path"]
    if not os.path.isabs(out_path):
        out_path = os.path.join(os.path.dirname(__file__), out_path)
    os.makedirs(ARCHIVE_DIR, exist_ok=True)

    counter = {"n": 0}
    quit_evt = threading.Event()

    def capture():
        frame = grab.grab_bgr(box)
        cv2.imwrite(out_path, frame)
        counter["n"] += 1
        archive = os.path.join(ARCHIVE_DIR, f"icon_{counter['n']:03d}.png")
        cv2.imwrite(archive, frame)
        feedback.beep_capture()
        feedback.status(f"  saved {out_path}  (#{counter['n']}, also {archive})",
                        "green")

    feedback.status("=" * 56, "grey")
    feedback.status("Template capture ready.", "cyan")
    feedback.status(f"  ROI: {box['width']}x{box['height']} @ "
                    f"({box['left']},{box['top']})", "grey")
    feedback.status("  Cast in D4, then press F7 the moment the icon shows.",
                    "yellow")
    feedback.status("  Press F9 here (or Ctrl+C) to finish.", "yellow")
    feedback.status("=" * 56, "grey")

    add_hotkey(cfg["keys"]["capture_template"], capture)
    add_hotkey(cfg["keys"]["quit"], quit_evt.set)

    try:
        while not quit_evt.is_set():
            time.sleep(0.05)
    except KeyboardInterrupt:
        pass
    grab.close()
    feedback.status(f"Done. {counter['n']} grab(s) captured.", "cyan")


if __name__ == "__main__":
    main()
