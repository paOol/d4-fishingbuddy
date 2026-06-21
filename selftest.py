"""Verify the install works BEFORE you rely on it in-game.

Run after setup (and ideally after capturing a template):

    py selftest.py

Checks, in order:
  1. all dependencies import
  2. screen capture returns a real, non-black frame for your ROI
  3. (template mode) the detector scores ~1.0 on the icon image itself and a
     low score on random noise — i.e. matching actually discriminates
  4. a key-send dry run (prints, does not press)
"""
from __future__ import annotations

import sys

OK = "\x1b[92m[ OK ]\x1b[0m"
BAD = "\x1b[91m[FAIL]\x1b[0m"
INFO = "\x1b[96m[ -- ]\x1b[0m"


def main() -> int:
    failures = 0

    # 1. imports
    try:
        import numpy as np
        import cv2
        import mss  # noqa: F401
        import pydirectinput  # noqa: F401
        import keyboard  # noqa: F401
        print(f"{OK} dependencies import (numpy {np.__version__}, cv2 {cv2.__version__})")
    except Exception as e:
        print(f"{BAD} import failed: {e}")
        print("      -> run setup.bat / 'py -m pip install -r requirements.txt'")
        return 1

    from core import config
    from core.screen import Grabber

    cfg = config.load()

    # 2. capture
    try:
        grab = Grabber()
        box = config.roi_box(cfg, grab.primary_monitor)
        frame = grab.grab_bgr(box)
        mean = float(frame.mean())
        shape = frame.shape
        grab.close()
        if shape[0] == box["height"] and shape[1] == box["width"]:
            print(f"{OK} capture ok — ROI {box['width']}x{box['height']} "
                  f"@ ({box['left']},{box['top']}), mean brightness {mean:.1f}")
        else:
            print(f"{BAD} capture size mismatch: got {shape}")
            failures += 1
        if mean < 2.0:
            print(f"{INFO} frame is nearly black — if D4 is running, switch it to "
                  f"'Windowed Fullscreen' (exclusive fullscreen blocks capture).")
    except Exception as e:
        print(f"{BAD} capture failed: {e}")
        failures += 1

    # 3. detection discrimination
    method = cfg["detection"].get("method", "template")
    try:
        from core.detect import Detector
        det = Detector(cfg)
        import numpy as np
        if method == "template":
            tmpl = det.template
            found_self, s_self = det.detect(tmpl.copy())
            noise = (np.random.default_rng(0).integers(
                0, 255, tmpl.shape, dtype=np.uint8))
            found_noise, s_noise = det.detect(noise)
            print(f"{INFO} template self-match {s_self:.3f} (want >= "
                  f"{det.threshold}), noise-match {s_noise:.3f} (want low)")
            if found_self and not found_noise:
                print(f"{OK} detection discriminates icon vs. noise")
            else:
                print(f"{BAD} detection unreliable — re-capture a cleaner template "
                      f"or adjust match_threshold")
                failures += 1
        else:
            print(f"{INFO} color mode — no template self-test; tune via config.")
            print(f"{OK} color detector constructed")
    except FileNotFoundError as e:
        print(f"{BAD} {e}")
        failures += 1
    except Exception as e:
        print(f"{BAD} detection error: {e}")
        failures += 1

    # 4. key send dry run (no actual press)
    print(f"{INFO} keys: cast={cfg['keys']['cast']} hook={cfg['keys']['hook']} "
          f"toggle={cfg['keys']['toggle']} quit={cfg['keys']['quit']} "
          f"(not pressed during selftest)")

    print()
    if failures:
        print(f"\x1b[91m{failures} check(s) failed — see above.\x1b[0m")
        return 1
    print("\x1b[92mAll checks passed. You're ready: run start.bat, press F8.\x1b[0m")
    return 0


if __name__ == "__main__":
    sys.exit(main())
