from __future__ import annotations

import tkinter as tk
from tkinter import font as tkfont
from typing import Callable

import mss
import numpy as np
from PIL import Image, ImageTk

from core.config import load_config, save_config
from core.pump_detector import PumpDetector


class PumpCalibrator:
    MIN_SIZE = 12
    OVERLAY_ALPHA = 0.35
    SELECTION_COLOR = "#66bb6a"
    EXISTING_COLOR = "#ffb74d"

    def __init__(self, on_done: Callable[[bool], None] | None = None) -> None:
        self.config = load_config()
        self.on_done = on_done
        self.root = tk.Tk()
        self.root.title("Pump Calibrator")
        self.root.attributes("-fullscreen", True)
        self.root.attributes("-topmost", True)
        self.root.attributes("-alpha", self.OVERLAY_ALPHA)
        self.root.configure(cursor="crosshair")

        self.canvas = tk.Canvas(
            self.root,
            highlightthickness=0,
            bg="black",
        )
        self.canvas.pack(fill="both", expand=True)

        self._start: tuple[int, int] | None = None
        self._selection_id: int | None = None
        self._existing_id: int | None = None
        self._selection: dict[str, int] | None = None

        self._build_hint()
        self._draw_existing_region()
        self._bind_events()

    def _build_hint(self) -> None:
        hint = tk.Toplevel(self.root)
        hint.overrideredirect(True)
        hint.attributes("-topmost", True)
        hint.configure(bg="#1a1a2e")

        text_font = tkfont.Font(family="Segoe UI", size=11)
        tk.Label(
            hint,
            text=(
                "Выдели кнопку Pump (зелёную или серую)\n"
                "Enter — сохранить   |   Esc — отмена   |   R — сброс"
            ),
            bg="#1a1a2e",
            fg="#eaeaea",
            font=text_font,
            padx=16,
            pady=10,
            justify="left",
        ).pack()

        hint.update_idletasks()
        hint.geometry(f"520x70+{hint.winfo_screenwidth() // 2 - 260}+20")
        self.hint = hint

    def _stored_region(self) -> dict[str, int] | None:
        region = self.config.get("afk", {}).get("pump_region")
        if not region:
            return None
        width = int(region.get("width", 0))
        height = int(region.get("height", 0))
        if width <= 0 or height <= 0:
            return None
        return {
            "left": int(region["left"]),
            "top": int(region["top"]),
            "width": width,
            "height": height,
        }

    def _screen_region(self) -> dict[str, int] | None:
        return self._stored_region()

    def _draw_existing_region(self) -> None:
        region = self._screen_region()
        if not region:
            return
        x1 = region["left"]
        y1 = region["top"]
        x2 = x1 + region["width"]
        y2 = y1 + region["height"]
        self._existing_id = self.canvas.create_rectangle(
            x1,
            y1,
            x2,
            y2,
            outline=self.EXISTING_COLOR,
            width=2,
            dash=(6, 4),
        )

    def _bind_events(self) -> None:
        self.canvas.bind("<ButtonPress-1>", self._on_press)
        self.canvas.bind("<B1-Motion>", self._on_drag)
        self.canvas.bind("<ButtonRelease-1>", self._on_release)
        self.root.bind("<Return>", lambda _event: self._save())
        self.root.bind("<Escape>", lambda _event: self._cancel())
        self.root.bind("<Key-r>", lambda _event: self._reset())
        self.root.bind("<Key-R>", lambda _event: self._reset())

    def _on_press(self, event: tk.Event) -> None:
        self._start = (event.x_root, event.y_root)
        if self._selection_id is not None:
            self.canvas.delete(self._selection_id)
            self._selection_id = None

    def _on_drag(self, event: tk.Event) -> None:
        if self._start is None:
            return
        x1, y1 = self._start
        x2, y2 = event.x_root, event.y_root
        if self._selection_id is not None:
            self.canvas.coords(self._selection_id, x1, y1, x2, y2)
        else:
            self._selection_id = self.canvas.create_rectangle(
                x1,
                y1,
                x2,
                y2,
                outline=self.SELECTION_COLOR,
                width=2,
            )

    def _on_release(self, event: tk.Event) -> None:
        if self._start is None:
            return
        x1, y1 = self._start
        x2, y2 = event.x_root, event.y_root
        left = min(x1, x2)
        top = min(y1, y2)
        width = abs(x2 - x1)
        height = abs(y2 - y1)
        self._start = None

        if width < self.MIN_SIZE or height < self.MIN_SIZE:
            if self._selection_id is not None:
                self.canvas.delete(self._selection_id)
                self._selection_id = None
            self._selection = None
            return

        self._selection = {
            "left": left,
            "top": top,
            "width": width,
            "height": height,
        }

    def _reset(self) -> None:
        self._start = None
        self._selection = None
        if self._selection_id is not None:
            self.canvas.delete(self._selection_id)
            self._selection_id = None

    def _cancel(self) -> None:
        self.hint.destroy()
        self.root.destroy()
        if self.on_done:
            self.on_done(False)

    def _save(self) -> None:
        screen_region = self._selection or self._screen_region()
        if not screen_region:
            return

        if "afk" not in self.config:
            self.config["afk"] = {}
        self.config["afk"]["pump_region"] = {
            "left": int(screen_region["left"]),
            "top": int(screen_region["top"]),
            "width": int(screen_region["width"]),
            "height": int(screen_region["height"]),
        }
        save_config(self.config)

        self.hint.destroy()
        self.root.withdraw()
        self._show_preview(self.config["afk"]["pump_region"])
        self.root.destroy()
        if self.on_done:
            self.on_done(True)

    def _show_preview(self, region: dict[str, int]) -> None:
        with mss.mss() as sct:
            shot = sct.grab(region)
        frame = np.array(shot, dtype=np.uint8)[:, :, :3]
        image = Image.fromarray(frame[:, :, ::-1])

        preview = tk.Tk()
        preview.title("Pump Preview")
        preview.attributes("-topmost", True)
        preview.configure(bg="#1a1a2e")

        title = tkfont.Font(family="Segoe UI", size=11, weight="bold")
        body = tkfont.Font(family="Segoe UI", size=10)

        tk.Label(
            preview,
            text="Область Pump сохранена в config.json",
            bg="#1a1a2e",
            fg="#eaeaea",
            font=title,
            pady=8,
        ).pack()

        info_text = (
            f"left={region['left']}  top={region['top']}  "
            f"width={region['width']}  height={region['height']}"
        )
        tk.Label(
            preview,
            text=info_text,
            bg="#1a1a2e",
            fg="#9aa0b5",
            font=body,
        ).pack()

        scale = min(1.0, 400 / max(image.width, 1), 200 / max(image.height, 1))
        display_size = (
            max(1, int(image.width * scale)),
            max(1, int(image.height * scale)),
        )
        display_image = image.resize(display_size, Image.Resampling.NEAREST)
        photo = ImageTk.PhotoImage(display_image)

        image_label = tk.Label(preview, image=photo, bg="#121223", padx=8, pady=8)
        image_label.image = photo
        image_label.pack(padx=12, pady=8)

        result_label = tk.Label(
            preview,
            text="",
            bg="#1a1a2e",
            fg="#66bb6a",
            font=body,
            justify="left",
        )
        result_label.pack(padx=12, pady=(0, 8))

        detector = PumpDetector(self.config.get("afk", {}))

        def test_color() -> None:
            ratio = detector.green_ratio(frame)
            ready = ratio >= detector.threshold
            state = "МОЖНО PUMP" if ready else "НЕЛЬЗЯ PUMP"
            result_label.configure(
                text=(
                    f"Статус: {state}\n"
                    f"Зелёных пикселей: {ratio * 100:.1f}% "
                    f"(порог {detector.threshold * 100:.1f}%)"
                )
            )

        button_row = tk.Frame(preview, bg="#1a1a2e")
        button_row.pack(pady=(0, 12))

        tk.Button(
            button_row,
            text="Test Pump",
            command=test_color,
            font=body,
            padx=12,
            pady=4,
        ).pack(side="left", padx=6)

        tk.Button(
            button_row,
            text="Закрыть",
            command=preview.destroy,
            font=body,
            padx=12,
            pady=4,
        ).pack(side="left", padx=6)

        test_color()
        preview.update_idletasks()
        width = max(preview.winfo_reqwidth(), 360)
        height = preview.winfo_reqheight()
        x = preview.winfo_screenwidth() // 2 - width // 2
        y = preview.winfo_screenheight() // 2 - height // 2
        preview.geometry(f"{width}x{height}+{x}+{y}")
        preview.mainloop()

    def run(self) -> bool:
        self.root.mainloop()
        return bool(self._selection)


def run_pump_calibrator() -> bool:
    result = {"saved": False}

    def on_done(saved: bool) -> None:
        result["saved"] = saved

    calibrator = PumpCalibrator(on_done=on_done)
    calibrator.run()
    return result["saved"]
