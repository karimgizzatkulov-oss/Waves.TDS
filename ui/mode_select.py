from __future__ import annotations

import tkinter as tk
from tkinter import font as tkfont
from tkinter import ttk
from typing import Callable

from core.i18n import get_language, set_language, t
from core.wave_data import list_mode_options


class ModeSelectDialog:
    BG = "#1a1a2e"
    FG = "#eaeaea"
    MUTED = "#9aa0b5"
    ACCENT = "#7c9cff"

    def __init__(
        self,
        default_mode: str,
        language: str | None = None,
        on_cancel: Callable[[], None] | None = None,
    ) -> None:
        if language:
            set_language(language)
        self.default_mode = default_mode
        self.on_cancel = on_cancel
        self.selected_mode: str | None = None
        self.options = list_mode_options()
        self.option_ids = [option["id"] for option in self.options]

        self.root = tk.Tk()
        self.root.title("TDS Wave Helper")
        self.root.configure(bg=self.BG)
        self.root.resizable(False, False)
        self.root.attributes("-topmost", True)

        self._title_label: tk.Label | None = None
        self._subtitle_label: tk.Label | None = None
        self._start_button: tk.Button | None = None
        self._cancel_button: tk.Button | None = None

        self._build_ui()
        self._center_window()
        self.root.protocol("WM_DELETE_WINDOW", self._cancel)

    def _build_ui(self) -> None:
        title_font = tkfont.Font(family="Segoe UI", size=14, weight="bold")
        body_font = tkfont.Font(family="Segoe UI", size=10)
        button_font = tkfont.Font(family="Segoe UI", size=10, weight="bold")

        frame = tk.Frame(self.root, bg=self.BG, padx=24, pady=20)
        frame.pack(fill="both", expand=True)

        self._title_label = tk.Label(
            frame,
            text=t("mode.title"),
            bg=self.BG,
            fg=self.FG,
            font=title_font,
        )
        self._title_label.pack(anchor="w")

        self._subtitle_label = tk.Label(
            frame,
            text=t("mode.subtitle"),
            bg=self.BG,
            fg=self.MUTED,
            font=body_font,
            wraplength=360,
            justify="left",
        )
        self._subtitle_label.pack(anchor="w", pady=(6, 14))

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Mode.TCombobox", padding=4)

        labels = [
            f"{option['name']}  ({t('mode.waves', count=option['max_wave'])})"
            for option in self.options
        ]
        self.display_values = labels

        default_index = 0
        if self.default_mode in self.option_ids:
            default_index = self.option_ids.index(self.default_mode)

        self.mode_var = tk.StringVar(value=labels[default_index])
        self.combo = ttk.Combobox(
            frame,
            textvariable=self.mode_var,
            values=labels,
            state="readonly",
            width=42,
            style="Mode.TCombobox",
        )
        self.combo.pack(fill="x")
        self.combo.bind("<Return>", lambda _event: self._start())

        button_row = tk.Frame(frame, bg=self.BG)
        button_row.pack(fill="x", pady=(18, 0))

        self._start_button = tk.Button(
            button_row,
            text=t("mode.start"),
            command=self._start,
            font=button_font,
            bg=self.ACCENT,
            fg="#ffffff",
            activebackground="#6b8cff",
            activeforeground="#ffffff",
            relief="flat",
            padx=18,
            pady=6,
            cursor="hand2",
        )
        self._start_button.pack(side="right")

        self._cancel_button = tk.Button(
            button_row,
            text=t("mode.cancel"),
            command=self._cancel,
            font=body_font,
            bg="#2a2a40",
            fg=self.FG,
            activebackground="#353550",
            activeforeground=self.FG,
            relief="flat",
            padx=14,
            pady=6,
            cursor="hand2",
        )
        self._cancel_button.pack(side="right", padx=(0, 8))

        self.root.bind("<Escape>", lambda _event: self._cancel())

    def _center_window(self) -> None:
        self.root.update_idletasks()
        width = max(self.root.winfo_reqwidth(), 400)
        height = self.root.winfo_reqheight()
        x = self.root.winfo_screenwidth() // 2 - width // 2
        y = self.root.winfo_screenheight() // 2 - height // 2
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def _selected_mode_id(self) -> str | None:
        label = self.mode_var.get()
        try:
            index = self.display_values.index(label)
        except ValueError:
            return None
        return self.option_ids[index]

    def _start(self) -> None:
        mode = self._selected_mode_id()
        if not mode:
            return
        self.selected_mode = mode
        self.root.destroy()

    def _cancel(self) -> None:
        self.selected_mode = None
        self.root.destroy()
        if self.on_cancel:
            self.on_cancel()

    def run(self) -> str | None:
        self.root.mainloop()
        return self.selected_mode


def ask_mode(default_mode: str, language: str | None = None) -> str | None:
    dialog = ModeSelectDialog(default_mode=default_mode, language=language or get_language())
    return dialog.run()
