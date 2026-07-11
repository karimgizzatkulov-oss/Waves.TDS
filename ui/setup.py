from __future__ import annotations

import tkinter as tk
from tkinter import font as tkfont
from tkinter import ttk
from typing import Callable

from core.config import is_pump_region_configured
from core.i18n import SUPPORTED_LANGUAGES, get_language, t
from core.wave_data import list_mode_options


class SetupPanel:
    def __init__(
        self,
        parent: tk.Misc,
        *,
        bg: str,
        fg: str,
        muted: str,
        accent: str,
        scroll_bg: str,
        wrap_width: int,
        on_calibrate_ocr: Callable[[], None],
        on_calibrate_pump: Callable[[], None],
        on_bind_window: Callable[[], None],
        on_change_mode: Callable[[], None],
        on_opacity_change: Callable[[float], None],
        on_language_change: Callable[[str], None],
    ) -> None:
        self._bg = bg
        self._fg = fg
        self._muted = muted
        self._accent = accent
        self._scroll_bg = scroll_bg
        self._wrap_width = wrap_width
        self._on_opacity_change = on_opacity_change
        self._on_language_change = on_language_change
        self._title_font = tkfont.Font(family="Segoe UI", size=10, weight="bold")
        self._body_font = tkfont.Font(family="Segoe UI", size=9)
        self._button_font = tkfont.Font(family="Segoe UI", size=10)

        self._title_label: tk.Label | None = None
        self._subtitle_label: tk.Label | None = None
        self._opacity_title: tk.Label | None = None
        self._language_title: tk.Label | None = None
        self._action_blocks: list[dict] = []
        self._status_titles: dict[str, tk.Label] = {}

        scroll_outer = tk.Frame(parent, bg=bg)
        scroll_outer.pack(fill="both", expand=True)

        self.canvas = tk.Canvas(scroll_outer, bg=bg, highlightthickness=0, borderwidth=0)
        scrollbar = tk.Scrollbar(
            scroll_outer,
            orient="vertical",
            command=self.canvas.yview,
            bg="#2a2a44",
            troughcolor=bg,
            activebackground=accent,
        )
        self.content = tk.Frame(self.canvas, bg=bg)

        self.content.bind(
            "<Configure>",
            lambda _event: self.canvas.configure(scrollregion=self.canvas.bbox("all")),
        )
        canvas_window = self.canvas.create_window((0, 0), window=self.content, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        def on_canvas_configure(event: tk.Event) -> None:
            self.canvas.itemconfigure(canvas_window, width=event.width)

        self.canvas.bind("<Configure>", on_canvas_configure)

        self._title_label = tk.Label(
            self.content,
            text=t("setup.title"),
            bg=bg,
            fg=accent,
            font=tkfont.Font(family="Segoe UI", size=12, weight="bold"),
            anchor="w",
        )
        self._title_label.pack(fill="x", pady=(0, 4))

        self._subtitle_label = tk.Label(
            self.content,
            text=t("setup.subtitle"),
            bg=bg,
            fg=muted,
            font=self._body_font,
            anchor="w",
            wraplength=wrap_width,
            justify="left",
        )
        self._subtitle_label.pack(fill="x", pady=(0, 10))

        self._add_action_button("mode", on_change_mode, accent, on_change_mode)
        self._mode_status = self._add_status_block("mode")

        self._add_action_button("ocr", on_calibrate_ocr, accent, on_calibrate_ocr)
        self._ocr_status = self._add_status_block("ocr")

        self._add_action_button("window", on_bind_window, accent, on_bind_window)
        self._window_status = self._add_status_block("window")

        self._add_action_button("pump", on_calibrate_pump, "#66bb6a", on_calibrate_pump)
        self._pump_status = self._add_status_block("pump")

        self._opacity_title = tk.Label(
            self.content,
            text=t("setup.opacity"),
            bg=bg,
            fg=fg,
            font=self._title_font,
            anchor="w",
        )
        self._opacity_title.pack(fill="x", pady=(12, 4))

        self.opacity_scale = tk.Scale(
            self.content,
            from_=0.45,
            to=1.0,
            resolution=0.05,
            orient="horizontal",
            bg=scroll_bg,
            fg=fg,
            troughcolor=bg,
            highlightthickness=0,
            activebackground=accent,
            command=self._handle_opacity,
            length=wrap_width,
        )
        self.opacity_scale.pack(fill="x", padx=4, pady=(0, 8))

        self._language_title = tk.Label(
            self.content,
            text=t("setup.language"),
            bg=bg,
            fg=fg,
            font=self._title_font,
            anchor="w",
        )
        self._language_title.pack(fill="x", pady=(12, 4))

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("SetupLang.TCombobox", padding=4)

        language_labels = [label for _code, label in SUPPORTED_LANGUAGES]
        self._language_codes = [code for code, _label in SUPPORTED_LANGUAGES]
        default_index = 0
        current = get_language()
        if current in self._language_codes:
            default_index = self._language_codes.index(current)

        self._language_var = tk.StringVar(value=language_labels[default_index])
        self.language_combo = ttk.Combobox(
            self.content,
            textvariable=self._language_var,
            values=language_labels,
            state="readonly",
            width=28,
            style="SetupLang.TCombobox",
        )
        self.language_combo.pack(fill="x", padx=4, pady=(0, 12))
        self.language_combo.bind("<<ComboboxSelected>>", self._handle_language_change)

    def _handle_opacity(self, value: str) -> None:
        self._on_opacity_change(float(value))

    def _handle_language_change(self, _event: tk.Event | None = None) -> None:
        label = self._language_var.get()
        try:
            index = list(self.language_combo["values"]).index(label)
        except ValueError:
            return
        code = self._language_codes[index]
        if code != get_language():
            self._on_language_change(code)

    def _setup_key(self, section: str, field: str) -> str:
        return f"setup.{section}.{field}"

    def _add_action_button(
        self,
        section: str,
        command: Callable[[], None],
        color: str,
        _command_ref: Callable[[], None],
    ) -> None:
        block = tk.Frame(self.content, bg=self._scroll_bg, padx=8, pady=8)
        block.pack(fill="x", pady=(0, 8))

        button = tk.Label(
            block,
            text=t(self._setup_key(section, "title")),
            bg=color,
            fg="#1a1a2e",
            font=self._button_font,
            cursor="hand2",
            padx=10,
            pady=6,
        )
        button.pack(anchor="w")
        button.bind("<Button-1>", lambda _event: command())

        description = tk.Label(
            block,
            text=t(self._setup_key(section, "desc")),
            bg=self._scroll_bg,
            fg=self._fg,
            font=self._body_font,
            anchor="w",
            wraplength=self._wrap_width - 16,
            justify="left",
        )
        description.pack(fill="x", pady=(6, 0))

        self._action_blocks.append({"section": section, "button": button, "description": description})

    def _add_status_block(self, section: str) -> tk.Label:
        title = tk.Label(
            self.content,
            text=t(self._setup_key(section, "status")),
            bg=self._scroll_bg,
            fg=self._fg,
            font=self._body_font,
            anchor="w",
            padx=8,
        )
        title.pack(fill="x")
        self._status_titles[section] = title

        label = tk.Label(
            self.content,
            text="—",
            bg=self._scroll_bg,
            fg=self._fg,
            font=self._body_font,
            anchor="w",
            wraplength=self._wrap_width,
            justify="left",
            padx=8,
        )
        label.pack(fill="x", pady=(0, 4))
        return label

    def apply_language(self) -> None:
        if self._title_label is not None:
            self._title_label.configure(text=t("setup.title"))
        if self._subtitle_label is not None:
            self._subtitle_label.configure(text=t("setup.subtitle"))
        if self._opacity_title is not None:
            self._opacity_title.configure(text=t("setup.opacity"))
        if self._language_title is not None:
            self._language_title.configure(text=t("setup.language"))

        for block in self._action_blocks:
            section = block["section"]
            block["button"].configure(text=t(self._setup_key(section, "title")))
            block["description"].configure(text=t(self._setup_key(section, "desc")))

        for section, title_label in self._status_titles.items():
            title_label.configure(text=t(self._setup_key(section, "status")))

        language_labels = [label for _code, label in SUPPORTED_LANGUAGES]
        current = get_language()
        index = self._language_codes.index(current) if current in self._language_codes else 0
        self.language_combo.configure(values=language_labels)
        self._language_var.set(language_labels[index])

    def refresh(self, config: dict) -> None:
        mode_id = str(config.get("mode", "hardcore"))
        mode_name = mode_id.title()
        for option in list_mode_options():
            if option["id"] == mode_id:
                mode_name = str(option["name"])
                break
        self._mode_status.configure(text=f"{mode_name} ({mode_id})")

        ocr = config.get("ocr_region", {})
        ocr_w = int(ocr.get("width", 0))
        ocr_h = int(ocr.get("height", 0))
        if ocr_w > 0 and ocr_h > 0:
            self._ocr_status.configure(
                text=(
                    f"left={ocr['left']}, top={ocr['top']}, "
                    f"{ocr_w}×{ocr_h}"
                )
            )
        else:
            self._ocr_status.configure(text=t("setup.not_configured"))

        window_cfg = config.get("window", {})
        if window_cfg.get("bind") and int(window_cfg.get("hwnd", 0) or 0) > 0:
            title = str(window_cfg.get("title", "Roblox")).strip() or "Roblox"
            self._window_status.configure(text=t("setup.window_bound", title=title))
        else:
            self._window_status.configure(text=t("setup.window_unbound"))

        pump = config.get("afk", {}).get("pump_region", {})
        pump_w = int(pump.get("width", 0))
        pump_h = int(pump.get("height", 0))
        if is_pump_region_configured(config):
            self._pump_status.configure(
                text=(
                    f"left={pump['left']}, top={pump['top']}, "
                    f"{pump_w}×{pump_h}"
                )
            )
        else:
            self._pump_status.configure(text=t("setup.not_configured"))

        opacity = float(config.get("overlay", {}).get("opacity", 0.85))
        self.opacity_scale.set(opacity)

        language = str(config.get("language", get_language()))
        if language in self._language_codes:
            index = self._language_codes.index(language)
            labels = [label for _code, label in SUPPORTED_LANGUAGES]
            self._language_var.set(labels[index])

    def refresh_scroll(self) -> None:
        self.content.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
