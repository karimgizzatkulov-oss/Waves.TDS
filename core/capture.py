from __future__ import annotations

from typing import Any

import mss
import numpy as np

from core.window_capture import capture_client_region
from core.window_target import WindowTarget


class ScreenCapture:
    def __init__(
        self,
        region: dict[str, int],
        window_target: WindowTarget | None = None,
    ) -> None:
        self._region = {
            "left": int(region["left"]),
            "top": int(region["top"]),
            "width": int(region["width"]),
            "height": int(region["height"]),
        }
        self._window_target = window_target
        self._sct = mss.mss()

    def update_region(self, region: dict[str, int]) -> None:
        self._region = {
            "left": int(region["left"]),
            "top": int(region["top"]),
            "width": int(region["width"]),
            "height": int(region["height"]),
        }

    def set_window_target(self, window_target: WindowTarget | None) -> None:
        self._window_target = window_target

    @property
    def region(self) -> dict[str, int]:
        return dict(self._region)

    def resolve_region(self, region: dict[str, int] | None = None) -> dict[str, int] | None:
        target = region or self._region
        if self._window_target and self._window_target.is_bound:
            return self._window_target.region_to_screen(target)
        return dict(target)

    def grab(self, region: dict[str, int] | None = None) -> np.ndarray | None:
        target = region or self._region
        if target["width"] <= 0 or target["height"] <= 0:
            return None

        if self._window_target and self._window_target.is_bound and self._window_target.is_valid():
            frame = capture_client_region(self._window_target.hwnd, target)
            if frame is not None:
                return frame

        capture_region = self.resolve_region(target)
        if capture_region is None:
            return None
        shot = self._sct.grab(capture_region)
        frame = np.array(shot, dtype=np.uint8)
        return frame[:, :, :3]

    def grab_wave_region(self) -> np.ndarray | None:
        return self.grab(self._region)
