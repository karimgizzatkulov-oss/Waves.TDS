from __future__ import annotations

import cv2
import numpy as np


class PumpDetector:
    def __init__(self, afk_config: dict) -> None:
        self.threshold = float(afk_config.get("green_ratio_threshold", 0.12))
        self._ready_streak = 0
        self._not_ready_streak = 0
        self._ready_frames = max(1, int(afk_config.get("ready_frames", 2)))

    def update_threshold(self, afk_config: dict) -> None:
        self.threshold = float(afk_config.get("green_ratio_threshold", 0.12))
        self._ready_frames = max(1, int(afk_config.get("ready_frames", 2)))

    def green_ratio(self, frame: np.ndarray) -> float:
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        lower = np.array([35, 70, 70], dtype=np.uint8)
        upper = np.array([90, 255, 255], dtype=np.uint8)
        mask = cv2.inRange(hsv, lower, upper)
        return float(mask.mean() / 255.0)

    def is_ready(self, frame: np.ndarray) -> bool:
        ratio = self.green_ratio(frame)
        if ratio >= self.threshold:
            self._ready_streak += 1
            self._not_ready_streak = 0
        else:
            self._not_ready_streak += 1
            self._ready_streak = 0
        return self._ready_streak >= self._ready_frames

    def reset(self) -> None:
        self._ready_streak = 0
        self._not_ready_streak = 0
