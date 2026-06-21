"""D4 FishingBuddy — main loop.

Safe automation for Diablo 4 fishing using ONLY screen capture + synthetic key
presses. No memory reading, no process injection, no game-file edits.

Cycle:  cast (F1)  ->  watch the region above the character for the fishing icon
        ->  the instant it appears, hook (A)  ->  wait  ->  repeat.

Hotkeys (global, work while D4 is focused):
    F8  toggle the bot ON / OFF
    F9  quit

Run as Administrator if D4/Battle.net is elevated, or your key presses won't
reach the game.
"""
from __future__ import annotations

import random
import threading
import time

from core import config, feedback
from core.screen import Grabber
from core.detect import Detector
from core.input import tap, add_hotkey, wait


class FishingBot:
    def __init__(self, cfg: dict):
        self.cfg = cfg
        self.keys = cfg["keys"]
        self.t = cfg["timing"]
        self.running = threading.Event()   # set => actively fishing
        self.quit = threading.Event()
        self.grabber = Grabber()
        self.detector = Detector(cfg)
        self.box = config.roi_box(cfg, self.grabber.primary_monitor)

    # --- timing helpers -------------------------------------------------
    def _jit(self, base: float) -> float:
        if self.t.get("humanize"):
            j = float(self.t.get("humanize_jitter", 0.0))
            return max(0.0, base + random.uniform(-j, j) * base)
        return base

    # --- hotkey callbacks ----------------------------------------------
    def toggle(self):
        if self.running.is_set():
            self.running.clear()
            feedback.status("● OFF — fishing paused (F8 to resume)", "yellow")
            feedback.beep_off()
        else:
            self.running.set()
            feedback.status("● ON — fishing armed", "green")
            feedback.beep_on()

    def request_quit(self):
        feedback.status("Quitting…", "grey")
        self.running.clear()
        self.quit.set()

    # --- core cycle -----------------------------------------------------
    def _wait_for_icon(self) -> bool:
        """Poll the ROI until the icon appears or we time out. Returns found."""
        deadline = time.time() + float(self.t["max_wait_for_icon"])
        poll = float(self.t["poll_interval"])
        best = 0.0
        while time.time() < deadline:
            if not self.running.is_set() or self.quit.is_set():
                return False
            frame = self.grabber.grab_bgr(self.box)
            found, score = self.detector.detect(frame)
            best = max(best, score)
            if found:
                feedback.status(f"  ✓ icon detected (score {score:.3f})", "green")
                return True
            time.sleep(poll)
        feedback.status(f"  … no bite within "
                        f"{self.t['max_wait_for_icon']}s (best {best:.3f}) — recasting",
                        "grey")
        return False

    def _one_cycle(self):
        feedback.status("→ cast (F1)", "cyan")
        tap(self.keys["cast"], jitter=0.03)
        feedback.beep_cast()

        # Let the bobber settle before we start watching.
        time.sleep(self._jit(float(self.t["settle_after_cast"])))
        if not self.running.is_set():
            return

        if self._wait_for_icon():
            rd = float(self.t.get("reaction_delay", 0.0))
            if rd:
                time.sleep(rd)
            tap(self.keys["hook"], jitter=0.03)
            feedback.status("→ hook (A) — fish on!", "green")
            feedback.beep_hook()
            time.sleep(self._jit(float(self.t["after_hook_delay"])))
        else:
            # Missed/no bite: brief pause, then recast.
            time.sleep(self._jit(float(self.t["recast_delay"])))

    def run(self):
        feedback.status("=" * 56, "grey")
        feedback.status("D4 FishingBuddy ready.", "cyan")
        feedback.status(f"  ROI: {self.box['width']}x{self.box['height']} @ "
                        f"({self.box['left']},{self.box['top']})", "grey")
        feedback.status(f"  detection: {self.detector.method}", "grey")
        feedback.status(f"  [{self.keys['toggle'].upper()}] toggle on/off   "
                        f"[{self.keys['quit'].upper()}] quit", "yellow")
        feedback.status("=" * 56, "grey")

        add_hotkey(self.keys["toggle"], self.toggle)
        add_hotkey(self.keys["quit"], self.request_quit)

        while not self.quit.is_set():
            if self.running.is_set():
                self._one_cycle()
            else:
                time.sleep(0.05)

        self.grabber.close()
        feedback.status("Stopped. Tight lines!", "cyan")


def main():
    cfg = config.load()
    bot = FishingBot(cfg)
    try:
        bot.run()
    except KeyboardInterrupt:
        bot.request_quit()


if __name__ == "__main__":
    main()
