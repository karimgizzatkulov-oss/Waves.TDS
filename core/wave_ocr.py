from __future__ import annotations

import re
from typing import Any

import cv2
import numpy as np

WAVE_PATTERN = re.compile(r"(\d+)\s*/\s*(\d+)")


class WaveOCR:
    def __init__(self, gpu: bool = False) -> None:
        self._reader: Any | None = None
        self._gpu = gpu

    def _get_reader(self) -> Any:
        if self._reader is None:
            import easyocr

            self._reader = easyocr.Reader(["en"], gpu=self._gpu, verbose=False)
        return self._reader

    @staticmethod
    def preprocess(frame: np.ndarray) -> np.ndarray:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        scaled = cv2.resize(gray, None, fx=2.0, fy=2.0, interpolation=cv2.INTER_CUBIC)
        _, binary = cv2.threshold(scaled, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        return binary

    def read_text(self, frame: np.ndarray) -> str:
        processed = self.preprocess(frame)
        reader = self._get_reader()
        results = reader.readtext(processed, detail=0, paragraph=True)
        return " ".join(str(item) for item in results)

    @staticmethod
    def parse_wave(text: str) -> tuple[int, int] | None:
        match = WAVE_PATTERN.search(text.replace("O", "0").replace("o", "0"))
        if not match:
            return None
        return int(match.group(1)), int(match.group(2))

    def read_wave(self, frame: np.ndarray) -> tuple[int, int] | None:
        return self.parse_wave(self.read_text(frame))


class WaveStabilizer:
    def __init__(self, required_frames: int = 3) -> None:
        self.required_frames = max(1, required_frames)
        self._candidate: tuple[int, int] | None = None
        self._streak = 0
        self._confirmed: tuple[int, int] | None = None

    @property
    def confirmed_wave(self) -> int | None:
        return self._confirmed[0] if self._confirmed else None

    @property
    def confirmed_max_wave(self) -> int | None:
        return self._confirmed[1] if self._confirmed else None

    def update(self, reading: tuple[int, int] | None) -> int | None:
        if reading is None:
            self._candidate = None
            self._streak = 0
            return self._confirmed[0] if self._confirmed else None

        if reading == self._candidate:
            self._streak += 1
        else:
            self._candidate = reading
            self._streak = 1

        if self._streak >= self.required_frames:
            self._confirmed = reading
        return self._confirmed[0] if self._confirmed else None

    def reset(self) -> None:
        self._candidate = None
        self._streak = 0
        self._confirmed = None
