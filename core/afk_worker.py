from __future__ import annotations

import queue
import time

import keyboard

from core.capture import ScreenCapture
from core.config import is_pump_region_configured
from core.pump_detector import PumpDetector


class AfkWorker:
    def __init__(self, config: dict, update_queue: queue.Queue) -> None:
        self.config = config
        self.update_queue = update_queue
        self.running = True
        self.enabled = False

        afk_config = config["afk"]
        self.capture = ScreenCapture(afk_config["pump_region"], window_target=None)
        self.detector = PumpDetector(afk_config)
        self._last_press_at = 0.0

    def update_config(self, config: dict) -> None:
        self.config = config
        afk_config = config["afk"]
        self.capture.update_region(afk_config["pump_region"])
        self.detector.update_threshold(afk_config)

    def set_enabled(self, enabled: bool) -> None:
        self.enabled = enabled
        self.detector.reset()
        self._notify_state()

    def toggle(self) -> bool:
        if not is_pump_region_configured(self.config):
            self.update_queue.put(("afk", "unconfigured", None))
            return False
        self.set_enabled(not self.enabled)
        return self.enabled

    def _notify_state(self, detail: str | None = None) -> None:
        if not is_pump_region_configured(self.config):
            self.update_queue.put(("afk", "unconfigured", detail))
            return
        if not self.enabled:
            self.update_queue.put(("afk", "off", detail))
            return
        self.update_queue.put(("afk", "on", detail))

    def _pump_burst(self, initial_ratio: float) -> dict[str, object]:
        afk_config = self.config["afk"]
        max_presses = max(1, int(afk_config.get("pump_burst_max", 8)))
        repeat_delay = max(0.05, afk_config.get("pump_repeat_delay_ms", 120) / 1000)

        presses = 0
        last_ratio = initial_ratio

        for attempt in range(max_presses):
            if attempt > 0:
                time.sleep(repeat_delay)
                frame = self.capture.grab()
                if frame is None:
                    break
                last_ratio = self.detector.green_ratio(frame)
                if last_ratio < self.detector.threshold:
                    break

            keyboard.press_and_release("e")
            presses += 1

        return {"presses": presses, "ratio": last_ratio}

    def run(self) -> None:
        self._notify_state()
        while self.running:
            afk_config = self.config["afk"]
            poll_seconds = max(0.05, afk_config.get("poll_ms", 150) / 1000)
            cooldown_seconds = max(0.1, afk_config.get("cooldown_ms", 500) / 1000)

            if not self.enabled or not is_pump_region_configured(self.config):
                time.sleep(poll_seconds)
                continue

            frame = self.capture.grab()
            if frame is None:
                time.sleep(poll_seconds)
                continue

            ready = self.detector.is_ready(frame)
            ratio = self.detector.green_ratio(frame)

            if ready:
                now = time.monotonic()
                if now - self._last_press_at >= cooldown_seconds:
                    press_info = self._pump_burst(ratio)
                    self._last_press_at = now
                    self.detector.reset()
                    self.update_queue.put(("afk", "pressed", press_info))
                else:
                    self.update_queue.put(("afk", "ready", {"ratio": ratio}))
            else:
                self.update_queue.put(("afk", "waiting", {"ratio": ratio}))

            time.sleep(poll_seconds)

    def stop(self) -> None:
        self.running = False
