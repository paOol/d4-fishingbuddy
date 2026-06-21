"""Fishing-icon detection. Pure pixel reading — template matching or color mask.

Both methods take an ROI image (BGR) and return (found: bool, score: float) so
the caller can log a confidence number while tuning.
"""
from __future__ import annotations

import os
from typing import Optional, Tuple

import cv2
import numpy as np


def load_template(path: str) -> Optional[np.ndarray]:
    if not path or not os.path.exists(path):
        return None
    return cv2.imread(path, cv2.IMREAD_COLOR)


def detect_template(roi_bgr: np.ndarray, template_bgr: np.ndarray,
                    threshold: float) -> Tuple[bool, float]:
    """Normalized-correlation template match. Robust against the busy terrain
    because it keys on the icon's exact shape/colors, not just hue."""
    th, tw = template_bgr.shape[:2]
    rh, rw = roi_bgr.shape[:2]
    if th > rh or tw > rw:
        # Template bigger than the search region — can't match. Tell the user.
        return False, 0.0
    res = cv2.matchTemplate(roi_bgr, template_bgr, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, _ = cv2.minMaxLoc(res)
    return max_val >= threshold, float(max_val)


def detect_color(roi_bgr: np.ndarray, lower_hsv, upper_hsv,
                 min_pixels: int) -> Tuple[bool, float]:
    """Count pixels inside an HSV band. Simple fallback when no template exists."""
    hsv = cv2.cvtColor(roi_bgr, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, np.array(lower_hsv, np.uint8),
                       np.array(upper_hsv, np.uint8))
    count = int(cv2.countNonZero(mask))
    return count >= min_pixels, float(count)


class Detector:
    """Bundles the configured detection method so the main loop stays clean."""

    def __init__(self, cfg: dict):
        det = cfg["detection"]
        self.method = det.get("method", "template")
        self.threshold = float(det.get("match_threshold", 0.72))
        c = det.get("color", {})
        self.lower = c.get("lower_hsv", [80, 70, 110])
        self.upper = c.get("upper_hsv", [105, 255, 255])
        self.min_pixels = int(c.get("min_pixels", 60))
        self.template = None
        if self.method == "template":
            self.template = load_template(det.get("template_path", ""))
            if self.template is None:
                raise FileNotFoundError(
                    "detection.method is 'template' but the template image was "
                    "not found. Run capture_template.py first, or set "
                    "detection.method to 'color' in config.json."
                )

    def detect(self, roi_bgr: np.ndarray) -> Tuple[bool, float]:
        if self.method == "color":
            return detect_color(roi_bgr, self.lower, self.upper, self.min_pixels)
        return detect_template(roi_bgr, self.template, self.threshold)
