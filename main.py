from __future__ import annotations

import argparse
import queue
import sys
import threading
import time
import tkinter as tk
from pathlib import Path

import keyboard

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.afk_worker import AfkWorker
from core.capture import ScreenCapture
from core.config import is_pump_region_configured, load_config, save_config
from core.i18n import set_language, t
from core.wave_data import WaveDatabase, WaveInfo
from core.wave_ocr import WaveOCR, WaveStabilizer
from core.window_target import WindowTarget
from ui.overlay import OverlayWindow


class WaveTracker:
    def __init__(
        self,
        config: dict,
        update_queue: queue.Queue,
        window_target: WindowTarget,
    ) -> None:
        self.config = config
        self.update_queue = update_queue
        self.running = True
        self.window_target = window_target

        self.capture = ScreenCapture(config["ocr_region"], window_target)
        self.ocr = WaveOCR(gpu=False)
        self.stabilizer = WaveStabilizer(config["ocr"].get("stable_frames", 3))
        self.database = WaveDatabase(config["mode"])

    def update_window_target(self, window_target: WindowTarget) -> None:
        self.window_target = window_target
        self.capture.set_window_target(window_target)
        self.window_target.update_config(self.config)

    def update_config(self, config: dict) -> None:
        self.config = config
        self.capture.update_region(config["ocr_region"])
        mode = str(config.get("mode", self.database.mode)).lower()
        if mode != self.database.mode:
            self.database = WaveDatabase(mode)
            self.stabilizer.reset()

    def run(self) -> None:
        poll_seconds = max(0.02, self.config["ocr"].get("poll_ms", 50) / 1000)
        last_reported: int | None = None

        self.update_queue.put(("status", "loading", t("overlay.loading_ocr")))

        while self.running:
            if self.window_target.is_bound and not self.window_target.is_valid():
                if last_reported is not None:
                    self.update_queue.put(("wave", None, None))
                    last_reported = None
                self.update_queue.put(("window", "lost", None))
                time.sleep(poll_seconds)
                continue

            frame = self.capture.grab_wave_region()
            if frame is None:
                if last_reported is not None:
                    self.update_queue.put(("wave", None, None))
                    last_reported = None
                self.update_queue.put(("window", "lost", None))
                time.sleep(poll_seconds)
                continue

            reading = self.ocr.read_wave(frame)
            wave = self.stabilizer.update(reading)

            if wave is None:
                if last_reported is not None:
                    self.update_queue.put(("wave", None, None))
                    last_reported = None
            elif wave != last_reported:
                info = self.database.get_wave(wave)
                self.update_queue.put(("wave", wave, info))
                last_reported = wave

            time.sleep(poll_seconds)

    def stop(self) -> None:
        self.running = False


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="TDS Wave Helper overlay")
    parser.add_argument(
        "--mode",
        choices=["easy", "casual", "intermediate", "molten", "fallen", "frost", "hardcore"],
        help="Game mode (overrides config.json)",
    )
    parser.add_argument(
        "--calibrate",
        action="store_true",
        help="Open OCR region calibrator and exit",
    )
    parser.add_argument(
        "--calibrate-pump",
        action="store_true",
        help="Open Pump button calibrator and exit",
    )
    parser.add_argument(
        "--no-prompt",
        action="store_true",
        help="Skip difficulty prompt on first launch only",
    )
    return parser.parse_args()


def prompt_mode(config: dict) -> dict | None:
    from ui.mode_select import ask_mode

    selected = ask_mode(
        config.get("mode", "hardcore"),
        language=str(config.get("language", "ru")),
    )
    if not selected:
        return None

    config["mode"] = selected
    save_config(config)
    return config


def run_session(config: dict) -> str:
    update_queue: queue.Queue = queue.Queue()
    window_target = WindowTarget(config)
    tracker = WaveTracker(config, update_queue, window_target)
    afk_worker = AfkWorker(config, update_queue)
    wave_thread = threading.Thread(target=tracker.run, daemon=True)
    afk_thread = threading.Thread(target=afk_worker.run, daemon=True)

    root = tk.Tk()
    root.withdraw()
    state = {"active": True}
    result = {"action": "quit"}
    hotkey_handle = None

    if not window_target.is_bound:
        from ui.window_select import ask_window_target

        choice = ask_window_target(parent=root, allow_unbind=True)
        if choice is False:
            root.destroy()
            return "quit"
        if choice is not None:
            window_target.bind(choice)
            save_config(config)

    root.deiconify()

    def persist_overlay_state() -> None:
        config["overlay"]["x"] = overlay.root.winfo_x()
        config["overlay"]["y"] = overlay.root.winfo_y()
        config["overlay"]["compact"] = overlay.compact
        save_config(config)

    def save_position(x: int, y: int) -> None:
        config["overlay"]["x"] = x
        config["overlay"]["y"] = y
        if window_target.is_bound:
            client = window_target.client_rect_screen()
            if client:
                config["overlay"]["window_offset_x"] = x - client["left"]
                config["overlay"]["window_offset_y"] = y - client["top"]
        save_config(config)

    def apply_window_binding(info) -> None:
        if info is False:
            return

        if info is None:
            window_target.unbind()
        else:
            window_target.bind(info)
            client = window_target.client_rect_screen()
            if client:
                overlay_cfg = config.setdefault("overlay", {})
                width = overlay.root.winfo_width()
                if width <= 1:
                    width = 320
                overlay_cfg["window_offset_x"] = max(0, client["width"] - width - 10)
                overlay_cfg["window_offset_y"] = 10
                overlay_cfg["follow_window"] = True

        save_config(config)
        window_target.update_config(config)
        tracker.update_window_target(window_target)
        afk_worker.update_config(config)
        overlay.config = config
        overlay.update_window_status(window_target)
        overlay.refresh_setup()

    def select_window() -> None:
        from ui.window_select import ask_window_target

        choice = ask_window_target(parent=root, allow_unbind=True)
        apply_window_binding(choice)

    def position_overlay_on_window() -> None:
        if not window_target.is_bound or not config["overlay"].get("follow_window", True):
            return
        client = window_target.client_rect_screen()
        if not client:
            overlay.update_window_status(window_target, lost=True)
            return

        overlay.update_window_status(window_target)
        ox = int(config["overlay"].get("window_offset_x", 0))
        oy = int(config["overlay"].get("window_offset_y", 0))
        if ox == 0 and oy == 0:
            width = overlay.root.winfo_width() or 320
            x = client["left"] + client["width"] - width - 10
            y = client["top"] + 10
        else:
            x = client["left"] + ox
            y = client["top"] + oy
        overlay.root.geometry(f"{overlay.root.winfo_width()}x{overlay.root.winfo_height()}+{x}+{y}")

    def finish(action: str) -> None:
        if not state["active"]:
            return
        state["active"] = False
        result["action"] = action
        tracker.stop()
        afk_worker.stop()
        if hotkey_handle is not None:
            keyboard.remove_hotkey(hotkey_handle)
        persist_overlay_state()
        root.quit()

    def close_app() -> None:
        finish("quit")

    def end_run() -> None:
        finish("restart")

    def toggle_afk() -> None:
        afk_worker.toggle()

    def reload_config() -> None:
        refreshed = load_config()
        config.clear()
        config.update(refreshed)
        set_language(str(config.get("language", "ru")))
        window_target.update_config(config)
        tracker.update_config(config)
        afk_worker.update_config(config)
        overlay.config = config
        overlay.apply_language()
        wave_num = overlay._last_wave_num
        if wave_num is not None:
            info = WaveDatabase(str(config.get("mode", "hardcore"))).get_wave(wave_num)
            overlay.update_wave(info, wave_num if info else None)
        else:
            overlay.refresh_localized_wave()
        overlay.refresh_setup()

    def run_calibrator_hidden(run_fn) -> bool:
        overlay.root.withdraw()
        try:
            return bool(run_fn())
        finally:
            overlay.root.deiconify()
            overlay.root.lift()
            overlay.root.attributes("-topmost", True)

    def calibrate_ocr() -> None:
        from ui.calibrate import run_calibrator

        if run_calibrator_hidden(run_calibrator):
            reload_config()

    def calibrate_pump() -> None:
        from ui.calibrate_pump import run_pump_calibrator

        was_enabled = afk_worker.enabled
        if was_enabled:
            afk_worker.set_enabled(False)

        if run_calibrator_hidden(run_pump_calibrator):
            reload_config()

        if was_enabled and is_pump_region_configured(config):
            afk_worker.set_enabled(True)

    def change_mode() -> None:
        from ui.mode_select import ask_mode

        overlay.root.withdraw()
        try:
            selected = ask_mode(
                config.get("mode", "hardcore"),
                language=str(config.get("language", "ru")),
            )
        finally:
            overlay.root.deiconify()
            overlay.root.lift()
            overlay.root.attributes("-topmost", True)

        if not selected or selected == config.get("mode"):
            return

        config["mode"] = selected
        save_config(config)
        tracker.update_config(config)
        overlay.config = config
        overlay.refresh_setup()
        overlay.title_label.configure(text=WaveDatabase(selected).mode_name)

    def set_opacity(value: float) -> None:
        config.setdefault("overlay", {})["opacity"] = round(value, 2)
        overlay.root.attributes("-alpha", value)
        save_config(config)

    def change_language(code: str) -> None:
        set_language(code)
        config["language"] = code
        save_config(config)
        overlay.config = config
        overlay.apply_language()
        wave_num = overlay._last_wave_num
        if wave_num is not None:
            info = WaveDatabase(str(config.get("mode", "hardcore"))).get_wave(wave_num)
            overlay.update_wave(info, wave_num if info else None)
        else:
            overlay.refresh_localized_wave()

    overlay = OverlayWindow(
        root,
        config,
        close_app,
        save_position,
        on_end=end_run,
        on_afk_toggle=toggle_afk,
        on_calibrate_ocr=calibrate_ocr,
        on_calibrate_pump=calibrate_pump,
        on_change_mode=change_mode,
        on_opacity_change=set_opacity,
        on_window_select=select_window,
        on_language_change=change_language,
    )
    overlay.update_window_status(window_target)
    overlay.refresh_setup()
    wave_thread.start()
    afk_thread.start()

    hotkey_name = str(config.get("afk", {}).get("hotkey", "f8")).lower()

    def on_hotkey() -> None:
        if state["active"]:
            root.after(0, toggle_afk)

    try:
        hotkey_handle = keyboard.add_hotkey(hotkey_name, on_hotkey, suppress=False)
    except Exception:
        hotkey_handle = None

    def poll_updates() -> None:
        if not state["active"]:
            return

        try:
            while True:
                kind, wave, payload = update_queue.get_nowait()
                if kind == "status":
                    if isinstance(payload, str):
                        overlay.status_label.configure(text=payload)
                    else:
                        overlay.show_scanning()
                elif kind == "wave":
                    overlay.update_wave(payload if isinstance(payload, WaveInfo) else None, wave)
                elif kind == "afk":
                    overlay.update_afk(wave, payload if isinstance(payload, dict) else None)
                elif kind == "window":
                    overlay.update_window_status(window_target, lost=(wave == "lost"))
        except queue.Empty:
            pass

        position_overlay_on_window()
        root.after(50, poll_updates)

    root.after(50, poll_updates)
    root.mainloop()

    try:
        root.destroy()
    except tk.TclError:
        pass

    wave_thread.join(timeout=2)
    afk_thread.join(timeout=2)
    return result["action"]


def main() -> None:
    args = parse_args()
    if args.calibrate:
        from ui.calibrate import run_calibrator

        run_calibrator()
        return
    if args.calibrate_pump:
        from ui.calibrate_pump import run_pump_calibrator

        run_pump_calibrator()
        return

    config = load_config()
    set_language(str(config.get("language", "ru")))
    skip_prompt_once = bool(args.mode or args.no_prompt)
    if args.mode:
        config["mode"] = args.mode

    while True:
        if not skip_prompt_once:
            config = prompt_mode(config)
            if config is None:
                return
        skip_prompt_once = False

        action = run_session(config)
        if action == "quit":
            return


if __name__ == "__main__":
    main()
