from __future__ import annotations

import tkinter as tk
from tkinter import font as tkfont
from typing import Callable

from core.i18n import t
from core.wave_data import WaveInfo
from ui.enemy_popup import close_enemy_popup, show_enemy_popup
from ui.help import build_help_panel, populate_help_content
from ui.setup import SetupPanel


class OverlayWindow:
    BG = "#1a1a2e"
    FG = "#eaeaea"
    MUTED = "#9aa0b5"
    ACCENT = "#7c9cff"
    SCROLL_BG = "#121223"
    WRAP_WIDTH = 300

    def __init__(
        self,
        root: tk.Tk,
        config: dict,
        on_close: Callable[[], None],
        on_position_change: Callable[[int, int], None],
        on_end: Callable[[], None] | None = None,
        on_afk_toggle: Callable[[], None] | None = None,
        on_calibrate_ocr: Callable[[], None] | None = None,
        on_calibrate_pump: Callable[[], None] | None = None,
        on_change_mode: Callable[[], None] | None = None,
        on_opacity_change: Callable[[float], None] | None = None,
        on_window_select: Callable[[], None] | None = None,
        on_language_change: Callable[[str], None] | None = None,
    ) -> None:
        self.root = root
        self.config = config
        self.on_close = on_close
        self.on_end = on_end
        self.on_position_change = on_position_change
        self.on_afk_toggle = on_afk_toggle
        self.on_calibrate_ocr = on_calibrate_ocr
        self.on_calibrate_pump = on_calibrate_pump
        self.on_change_mode = on_change_mode
        self.on_opacity_change = on_opacity_change
        self.on_window_select = on_window_select
        self.on_language_change = on_language_change
        self.compact = bool(config["overlay"].get("compact", False))
        self._afk_enabled = False
        self._follow_window = bool(config["overlay"].get("follow_window", True))
        self._active_tab = "wave"
        self._enemy_traits: dict[str, list[str]] = {}
        self._last_wave: WaveInfo | None = None
        self._last_wave_num: int | None = None
        self._unrecognized = False
        self._afk_state = "unconfigured"
        self._afk_detail: dict | None = None
        self._body_font = tkfont.Font(family="Segoe UI", size=10)
        self._small_font = tkfont.Font(family="Segoe UI", size=9)

        self.root.title("TDS Wave Helper")
        self.root.configure(bg=self.BG)
        self.root.attributes("-topmost", True)
        self.root.overrideredirect(True)
        self.root.geometry(
            f"340x480+{config['overlay']['x']}+{config['overlay']['y']}"
        )
        self.root.attributes("-alpha", float(config["overlay"].get("opacity", 0.85)))

        self._drag_offset: tuple[int, int] | None = None
        self._build_ui()
        self._bind_events()
        self.show_waiting()

    def _build_ui(self) -> None:
        self.header = tk.Frame(self.root, bg=self.BG, padx=12, pady=8)
        self.header.pack(fill="x")

        title_font = tkfont.Font(family="Segoe UI", size=11, weight="bold")
        body_font = tkfont.Font(family="Segoe UI", size=10)
        small_font = tkfont.Font(family="Segoe UI", size=9)
        wave_font = tkfont.Font(family="Segoe UI", size=16, weight="bold")

        self.title_label = tk.Label(
            self.header,
            text="TDS Helper",
            bg=self.BG,
            fg=self.FG,
            font=title_font,
            anchor="w",
        )
        self.title_label.pack(side="left", fill="x", expand=True)

        self.end_button = tk.Label(
            self.header,
            text="END",
            bg=self.BG,
            fg="#ffb74d",
            font=title_font,
            cursor="hand2",
        )
        self.end_button.pack(side="right", padx=(0, 10))

        self.setup_button = tk.Label(
            self.header,
            text="SETUP",
            bg=self.BG,
            fg="#ffb74d",
            font=title_font,
            cursor="hand2",
        )
        self.setup_button.pack(side="right", padx=(0, 10))

        self.window_button = tk.Label(
            self.header,
            text="WIN",
            bg=self.BG,
            fg=self.ACCENT,
            font=title_font,
            cursor="hand2",
        )
        self.window_button.pack(side="right", padx=(0, 10))

        self.close_button = tk.Label(
            self.header,
            text="×",
            bg=self.BG,
            fg=self.MUTED,
            font=title_font,
            cursor="hand2",
        )
        self.close_button.pack(side="right")

        self.body = tk.Frame(self.root, bg=self.BG, padx=12, pady=4)
        self.body.pack(fill="both", expand=True)

        self.wave_label = tk.Label(
            self.body,
            text="Wave —",
            bg=self.BG,
            fg=self.ACCENT,
            font=wave_font,
            anchor="w",
        )
        self.wave_label.pack(fill="x", pady=(0, 2))

        self.phase_label = tk.Label(
            self.body,
            text="",
            bg=self.BG,
            fg=self.MUTED,
            font=body_font,
            anchor="w",
        )
        self.phase_label.pack(fill="x", pady=(0, 6))

        self.tab_bar = tk.Frame(self.body, bg=self.BG)
        self.tab_bar.pack(fill="x", pady=(0, 4))

        self.wave_tab_button = tk.Label(
            self.tab_bar,
            text=t("overlay.tab.wave"),
            bg="#2a2a44",
            fg=self.ACCENT,
            font=body_font,
            cursor="hand2",
            padx=12,
            pady=4,
        )
        self.wave_tab_button.pack(side="left")

        self.help_tab_button = tk.Label(
            self.tab_bar,
            text=t("overlay.tab.help"),
            bg=self.BG,
            fg=self.MUTED,
            font=body_font,
            cursor="hand2",
            padx=12,
            pady=4,
        )
        self.help_tab_button.pack(side="left")

        self.wave_panel = tk.Frame(self.body, bg=self.BG)
        self.wave_panel.pack(fill="both", expand=True)

        scroll_outer = tk.Frame(self.wave_panel, bg=self.BG)
        scroll_outer.pack(fill="both", expand=True)

        self.scroll_canvas = tk.Canvas(
            scroll_outer,
            bg=self.BG,
            highlightthickness=0,
            borderwidth=0,
        )
        self.scrollbar = tk.Scrollbar(
            scroll_outer,
            orient="vertical",
            command=self.scroll_canvas.yview,
            bg="#2a2a44",
            troughcolor=self.BG,
            activebackground=self.ACCENT,
        )
        self.scrollable_frame = tk.Frame(self.scroll_canvas, bg=self.BG)

        self.scrollable_frame.bind("<Configure>", self._on_scroll_frame_configure)
        self._canvas_window = self.scroll_canvas.create_window(
            (0, 0),
            window=self.scrollable_frame,
            anchor="nw",
        )
        self.scroll_canvas.configure(yscrollcommand=self.scrollbar.set)
        self.scroll_canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        self.scroll_canvas.bind("<Configure>", self._on_canvas_configure)

        content = self.scrollable_frame

        self.status_label = tk.Label(
            content,
            text=t("overlay.waiting"),
            bg=self.BG,
            fg=self.MUTED,
            font=body_font,
            anchor="w",
        )
        self.status_label.pack(fill="x")

        self.window_status_label = tk.Label(
            content,
            text=t("overlay.window_fullscreen"),
            bg=self.BG,
            fg=self.MUTED,
            font=small_font,
            anchor="w",
        )
        self.window_status_label.pack(fill="x", pady=(0, 4))

        self.danger_label = tk.Label(
            content,
            text="",
            bg=self.BG,
            fg=self.FG,
            font=body_font,
            anchor="w",
        )
        self.danger_label.pack(fill="x", pady=(8, 0))

        self.danger_detail_label = tk.Label(
            content,
            text="",
            bg=self.BG,
            fg=self.MUTED,
            font=small_font,
            anchor="w",
            wraplength=self.WRAP_WIDTH,
            justify="left",
        )
        self.danger_detail_label.pack(fill="x", pady=(2, 0))

        self.enemies_title = tk.Label(
            content,
            text=t("overlay.enemies"),
            bg=self.BG,
            fg=self.MUTED,
            font=body_font,
            anchor="w",
        )
        self.enemies_title.pack(fill="x", pady=(10, 2))

        self.enemies_box = tk.Frame(content, bg=self.SCROLL_BG, padx=8, pady=8)
        self.enemies_box.pack(fill="x")

        self.enemies_list_frame = tk.Frame(self.enemies_box, bg=self.SCROLL_BG)
        self.enemies_list_frame.pack(fill="x")

        self.skip_label = tk.Label(
            content,
            text="",
            bg=self.BG,
            fg=self.FG,
            font=body_font,
            anchor="w",
            wraplength=self.WRAP_WIDTH,
            justify="left",
        )
        self.skip_label.pack(fill="x", pady=(8, 0))

        self.next_title = tk.Label(
            content,
            text=t("overlay.next_wave"),
            bg=self.BG,
            fg=self.MUTED,
            font=body_font,
            anchor="w",
        )
        self.next_title.pack(fill="x", pady=(8, 2))

        self.next_box = tk.Frame(content, bg=self.SCROLL_BG, padx=8, pady=6)
        self.next_box.pack(fill="x", pady=(2, 0))

        self.next_content_frame = tk.Frame(self.next_box, bg=self.SCROLL_BG)
        self.next_content_frame.pack(fill="x")

        self.afk_row = tk.Frame(content, bg=self.BG)
        self.afk_row.pack(fill="x", pady=(10, 0))

        self.afk_button = tk.Label(
            self.afk_row,
            text="AFK: OFF",
            bg="#2a2a44",
            fg=self.MUTED,
            font=body_font,
            cursor="hand2",
            padx=10,
            pady=4,
        )
        self.afk_button.pack(side="left")

        self.afk_status_label = tk.Label(
            content,
            text=t("overlay.afk.unconfigured"),
            bg=self.BG,
            fg=self.MUTED,
            font=small_font,
            anchor="w",
            wraplength=self.WRAP_WIDTH,
            justify="left",
        )
        self.afk_status_label.pack(fill="x", pady=(4, 8))

        self.hint_label = tk.Label(
            self.root,
            text=t("overlay.hint"),
            bg=self.BG,
            fg=self.MUTED,
            font=small_font,
            anchor="w",
            padx=12,
            pady=6,
        )
        self.hint_label.pack(fill="x")

        self._bind_mousewheel(self.scroll_canvas)
        self._bind_mousewheel(self.scrollable_frame)
        self._bind_mousewheel(self.wave_panel)
        self._bind_mousewheel(self.enemies_box)
        self._bind_mousewheel(self.enemies_list_frame)
        self._bind_mousewheel(self.next_box)
        self._bind_mousewheel(self.next_content_frame)
        self._bind_scroll_to_children(self.scrollable_frame)

        self.help_panel = tk.Frame(self.body, bg=self.BG)
        self.help_canvas, self.help_content = build_help_panel(
            self.help_panel,
            bg=self.BG,
            fg=self.FG,
            muted=self.MUTED,
            accent=self.ACCENT,
            scroll_bg=self.SCROLL_BG,
            wrap_width=self.WRAP_WIDTH,
        )
        self._bind_mousewheel(self.help_canvas)
        self._bind_mousewheel(self.help_content)
        self._bind_scroll_to_children(self.help_content)

        self.setup_panel = tk.Frame(self.body, bg=self.BG)
        noop = lambda: None
        self.setup_view = SetupPanel(
            self.setup_panel,
            bg=self.BG,
            fg=self.FG,
            muted=self.MUTED,
            accent=self.ACCENT,
            scroll_bg=self.SCROLL_BG,
            wrap_width=self.WRAP_WIDTH,
            on_calibrate_ocr=self.on_calibrate_ocr or noop,
            on_calibrate_pump=self.on_calibrate_pump or noop,
            on_bind_window=self.on_window_select or noop,
            on_change_mode=self.on_change_mode or noop,
            on_opacity_change=self.on_opacity_change or (lambda _value: None),
            on_language_change=self.on_language_change or (lambda _code: None),
        )
        self.setup_view.refresh(self.config)
        self._bind_mousewheel(self.setup_view.canvas)
        self._bind_mousewheel(self.setup_view.content)
        self._bind_scroll_to_children(self.setup_view.content)

        self.wave_tab_button.bind("<Button-1>", lambda _event: self._select_tab("wave"))
        self.help_tab_button.bind("<Button-1>", lambda _event: self._select_tab("help"))

    def _bind_scroll_to_children(self, widget: tk.Misc) -> None:
        for child in widget.winfo_children():
            self._bind_mousewheel(child)
            self._bind_scroll_to_children(child)

    def _on_scroll_frame_configure(self, _event: tk.Event) -> None:
        self.scroll_canvas.configure(scrollregion=self.scroll_canvas.bbox("all"))

    def _on_canvas_configure(self, event: tk.Event) -> None:
        self.scroll_canvas.itemconfigure(self._canvas_window, width=event.width)

    def _bind_mousewheel(self, widget: tk.Misc) -> None:
        widget.bind("<MouseWheel>", self._on_mousewheel)

    def _on_mousewheel(self, event: tk.Event) -> None:
        if self.compact:
            return
        canvas = self.scroll_canvas
        if self._active_tab == "help":
            canvas = self.help_canvas
        elif self._active_tab == "setup":
            canvas = self.setup_view.canvas
        canvas.yview_scroll(int(-event.delta / 120), "units")

    def _select_tab(self, tab: str) -> None:
        if self.compact:
            tab = "wave"
        if tab not in {"wave", "help", "setup"}:
            return

        self._active_tab = tab
        active_bg = "#2a2a44"
        inactive_bg = self.BG

        self.wave_panel.pack_forget()
        self.help_panel.pack_forget()
        self.setup_panel.pack_forget()

        self.wave_tab_button.configure(bg=inactive_bg, fg=self.MUTED)
        self.help_tab_button.configure(bg=inactive_bg, fg=self.MUTED)
        self.setup_button.configure(bg=self.BG, fg="#ffb74d")

        if tab == "wave":
            self.wave_panel.pack(fill="both", expand=True)
            self.wave_tab_button.configure(bg=active_bg, fg=self.ACCENT)
            self._scroll_to_top()
        elif tab == "help":
            self.help_panel.pack(fill="both", expand=True)
            self.help_tab_button.configure(bg=active_bg, fg=self.ACCENT)
            self.help_canvas.yview_moveto(0)
        else:
            self.setup_panel.pack(fill="both", expand=True)
            self.setup_button.configure(bg=active_bg, fg="#ffb74d")
            self.refresh_setup()
            self.setup_view.canvas.yview_moveto(0)

        self._refresh_scroll_region()

    def refresh_setup(self) -> None:
        self.setup_view.refresh(self.config)
        self.setup_view.refresh_scroll()

    def apply_language(self) -> None:
        self.wave_tab_button.configure(text=t("overlay.tab.wave"))
        self.help_tab_button.configure(text=t("overlay.tab.help"))
        self.enemies_title.configure(text=t("overlay.enemies"))
        self.next_title.configure(text=t("overlay.next_wave"))
        self.hint_label.configure(text=t("overlay.hint"))
        self.setup_view.apply_language()
        populate_help_content(
            self.help_content,
            bg=self.BG,
            fg=self.FG,
            accent=self.ACCENT,
            scroll_bg=self.SCROLL_BG,
            wrap_width=self.WRAP_WIDTH,
        )
        self.setup_view.refresh(self.config)
        self.update_afk(self._afk_state, self._afk_detail)
        self._refresh_scroll_region()

    def refresh_localized_wave(self) -> None:
        if self._unrecognized:
            self.show_waiting(t("overlay.wave_unrecognized"), reset_state=False)
        elif self._last_wave is None and self._last_wave_num is None:
            self.show_waiting(reset_state=False)

    def _scroll_to_top(self) -> None:
        self.scroll_canvas.yview_moveto(0)

    def _refresh_scroll_region(self) -> None:
        self.scrollable_frame.update_idletasks()
        self.scroll_canvas.configure(scrollregion=self.scroll_canvas.bbox("all"))
        self.help_content.update_idletasks()
        self.help_canvas.configure(scrollregion=self.help_canvas.bbox("all"))
        self.setup_view.refresh_scroll()

    def _bind_events(self) -> None:
        for widget in (self.header, self.title_label):
            widget.bind("<ButtonPress-1>", self._start_drag)
            widget.bind("<B1-Motion>", self._on_drag)

        self.close_button.bind("<Button-1>", lambda _event: self.on_close())
        if self.on_end:
            self.end_button.bind("<Button-1>", lambda _event: self.on_end())
        if self.on_afk_toggle:
            self.afk_button.bind("<Button-1>", lambda _event: self.on_afk_toggle())
        self.setup_button.bind("<Button-1>", lambda _event: self._toggle_setup())
        if self.on_window_select:
            self.window_button.bind("<Button-1>", lambda _event: self.on_window_select())
        self.root.bind("<F1>", self._toggle_compact)
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def _toggle_setup(self) -> None:
        if self.compact:
            return
        if self._active_tab == "setup":
            self._select_tab("wave")
        else:
            self._select_tab("setup")

    def _start_drag(self, event: tk.Event) -> None:
        self._drag_offset = (event.x_root - self.root.winfo_x(), event.y_root - self.root.winfo_y())

    def _on_drag(self, event: tk.Event) -> None:
        if self._drag_offset is None:
            return
        if self._follow_window:
            self.set_follow_window(False)
        x = event.x_root - self._drag_offset[0]
        y = event.y_root - self._drag_offset[1]
        self.root.geometry(f"+{x}+{y}")

    def _save_position(self) -> None:
        if self._follow_window:
            return
        self.on_position_change(self.root.winfo_x(), self.root.winfo_y())

    def set_follow_window(self, enabled: bool) -> None:
        self._follow_window = enabled
        self.config.setdefault("overlay", {})["follow_window"] = enabled

    def _toggle_compact(self, _event: tk.Event | None = None) -> None:
        self.compact = not self.compact
        self.config["overlay"]["compact"] = self.compact
        self._apply_compact_mode()

    def _apply_compact_mode(self) -> None:
        hidden_in_compact = (
            self.tab_bar,
            self.setup_button,
            self.enemies_title,
            self.enemies_box,
            self.danger_detail_label,
            self.next_title,
            self.next_box,
            self.window_status_label,
            self.afk_row,
            self.afk_status_label,
            self.scrollbar,
            self.hint_label,
        )
        for widget in hidden_in_compact:
            if self.compact:
                widget.pack_forget()
            else:
                if widget is self.tab_bar:
                    widget.pack(fill="x", pady=(0, 4))
                elif widget is self.setup_button:
                    widget.pack(side="right", padx=(0, 10))
                elif widget is self.enemies_title:
                    widget.pack(fill="x", pady=(10, 2))
                elif widget is self.enemies_box:
                    widget.pack(fill="x")
                elif widget is self.danger_detail_label:
                    widget.pack(fill="x", pady=(2, 0))
                elif widget is self.next_title:
                    widget.pack(fill="x", pady=(8, 2))
                elif widget is self.next_box:
                    widget.pack(fill="x", pady=(2, 0))
                elif widget is self.window_status_label:
                    widget.pack(fill="x", pady=(0, 4))
                elif widget is self.afk_row:
                    widget.pack(fill="x", pady=(10, 0))
                elif widget is self.afk_status_label:
                    widget.pack(fill="x", pady=(4, 8))
                elif widget is self.scrollbar:
                    widget.pack(side="right", fill="y")
                elif widget is self.hint_label:
                    widget.pack(fill="x")

        if self.compact:
            self._select_tab("wave")
            self.root.geometry(f"280x230+{self.root.winfo_x()}+{self.root.winfo_y()}")
        else:
            self.root.geometry(f"340x480+{self.root.winfo_x()}+{self.root.winfo_y()}")
            self._scroll_to_top()
            self._refresh_scroll_region()

    def update_window_status(self, window_target, lost: bool = False) -> None:
        if not window_target.is_bound:
            self.window_status_label.configure(text=t("overlay.window_fullscreen"), fg=self.MUTED)
            self.window_button.configure(fg=self.ACCENT)
            self.set_follow_window(False)
            return

        self.set_follow_window(bool(self.config.get("overlay", {}).get("follow_window", True)))
        title = window_target.title() or "Roblox"
        short_title = title if len(title) <= 34 else title[:31] + "..."
        if lost or not window_target.is_valid():
            self.window_status_label.configure(
                text=t("overlay.window_lost", title=short_title),
                fg="#ff8a80",
            )
            self.window_button.configure(fg="#ff8a80")
            return

        self.window_status_label.configure(
            text=t("overlay.window_bound", title=short_title),
            fg="#9ad09a",
        )
        self.window_button.configure(fg="#9ad09a")

    def _clear_frame(self, frame: tk.Frame) -> None:
        for child in frame.winfo_children():
            child.destroy()

    def _enemy_suffix(self, enemy) -> str:
        from core.enemy_stats import EnemyStats

        parts: list[str] = []
        if enemy.modifiers:
            parts.append(f"({', '.join(enemy.modifiers)})")
        if enemy.hp is not None:
            parts.append(f"— {enemy.hp} HP")
        if enemy.defenses:
            parts.append(f"[{EnemyStats.format_defenses(enemy.defenses)}]")
        return " ".join(parts)

    def _open_enemy_info(self, enemy) -> None:
        show_enemy_popup(self.root, enemy, self._enemy_traits)

    def _render_enemy_lines(
        self,
        container: tk.Frame,
        enemies: tuple,
        *,
        name_color: str,
        empty_text: str = "—",
    ) -> None:
        self._clear_frame(container)
        if not enemies:
            tk.Label(
                container,
                text=empty_text,
                bg=self.SCROLL_BG,
                fg=self.FG,
                font=self._body_font,
                anchor="w",
            ).pack(fill="x")
            return

        for enemy in enemies:
            row = tk.Frame(container, bg=self.SCROLL_BG)
            row.pack(fill="x", anchor="w", pady=1)

            tk.Label(
                row,
                text=f"{enemy.count}x ",
                bg=self.SCROLL_BG,
                fg=self.FG,
                font=self._body_font,
                anchor="w",
            ).pack(side="left")

            name_label = tk.Label(
                row,
                text=enemy.type,
                bg=self.SCROLL_BG,
                fg=name_color,
                font=self._body_font,
                anchor="w",
                cursor="hand2",
                underline=True,
            )
            name_label.pack(side="left")
            name_label.bind("<Button-1>", lambda _event, item=enemy: self._open_enemy_info(item))

            suffix = self._enemy_suffix(enemy)
            if suffix:
                tk.Label(
                    row,
                    text=f" {suffix}",
                    bg=self.SCROLL_BG,
                    fg=self.FG,
                    font=self._body_font,
                    anchor="w",
                ).pack(side="left")

            self._bind_mousewheel(row)

    def _render_next_wave(self, info: WaveInfo) -> None:
        self._clear_frame(self.next_content_frame)

        if info.wave >= info.max_wave:
            lines = [t("overlay.final_wave")]
            if info.final_wave_tip:
                lines.append("")
                lines.append(info.final_wave_tip)
            tk.Label(
                self.next_content_frame,
                text="\n".join(lines),
                bg=self.SCROLL_BG,
                fg="#ffb74d",
                font=self._body_font,
                anchor="nw",
                justify="left",
                wraplength=self.WRAP_WIDTH,
            ).pack(fill="x", anchor="w")
            return

        tk.Label(
            self.next_content_frame,
            text=t("overlay.next_wave_num", wave=info.wave + 1),
            bg=self.SCROLL_BG,
            fg="#ffb74d",
            font=self._body_font,
            anchor="w",
        ).pack(fill="x", anchor="w")

        enemies_frame = tk.Frame(self.next_content_frame, bg=self.SCROLL_BG)
        enemies_frame.pack(fill="x", anchor="w")
        self._render_enemy_lines(
            enemies_frame,
            info.next_wave_enemies,
            name_color="#ffd180",
            empty_text="—",
        )

        if info.next_warnings:
            tk.Label(
                self.next_content_frame,
                text="",
                bg=self.SCROLL_BG,
            ).pack()
            tk.Label(
                self.next_content_frame,
                text=t("overlay.detection_needed"),
                bg=self.SCROLL_BG,
                fg=self.MUTED,
                font=self._body_font,
                anchor="w",
            ).pack(fill="x", anchor="w")
            for warning in info.next_warnings:
                tk.Label(
                    self.next_content_frame,
                    text=f"⚠ {warning}",
                    bg=self.SCROLL_BG,
                    fg="#ffb74d",
                    font=self._small_font,
                    anchor="nw",
                    justify="left",
                    wraplength=self.WRAP_WIDTH,
                ).pack(fill="x", anchor="w", pady=(2, 0))

    def show_waiting(self, message: str | None = None, *, reset_state: bool = True) -> None:
        if message is None:
            message = t("overlay.waiting")
        if reset_state:
            self._last_wave = None
            self._last_wave_num = None
            self._unrecognized = False
        self.status_label.configure(text=message)
        self.wave_label.configure(text="Wave —")
        self.phase_label.configure(text="")
        self.danger_label.configure(text="")
        self.danger_detail_label.configure(text="")
        self._render_enemy_lines(self.enemies_list_frame, (), name_color=self.ACCENT)
        self.skip_label.configure(text="")
        self._clear_frame(self.next_content_frame)
        tk.Label(
            self.next_content_frame,
            text="—",
            bg=self.SCROLL_BG,
            fg="#ffb74d",
            font=self._body_font,
            anchor="w",
        ).pack(fill="x")
        close_enemy_popup()
        self._scroll_to_top()
        self._refresh_scroll_region()

    def update_afk(self, state: str, detail: dict | None = None) -> None:
        self._afk_state = state
        self._afk_detail = detail
        ratio_text = ""
        if detail and "ratio" in detail:
            ratio_text = t("overlay.afk.ratio", percent=detail["ratio"] * 100)

        if state == "unconfigured":
            self._afk_enabled = False
            self.afk_button.configure(text="AFK: OFF", fg=self.MUTED, bg="#2a2a44")
            self.afk_status_label.configure(text=t("overlay.afk.unconfigured"))
            return

        if state == "off":
            self._afk_enabled = False
            self.afk_button.configure(text="AFK: OFF", fg=self.MUTED, bg="#2a2a44")
            self.afk_status_label.configure(text=t("overlay.afk.off", ratio=ratio_text))
            return

        self._afk_enabled = True
        self.afk_button.configure(text="AFK: ON", fg="#1a1a2e", bg="#66bb6a")

        if state == "pressed":
            presses = int(detail.get("presses", 1)) if detail else 1
            press_text = "E" if presses == 1 else f"E x{presses}"
            self.afk_status_label.configure(
                text=t("overlay.afk.pressed", presses=press_text, ratio=ratio_text)
            )
        elif state == "ready":
            self.afk_status_label.configure(text=t("overlay.afk.on_ready", ratio=ratio_text))
        elif state == "waiting":
            self.afk_status_label.configure(text=t("overlay.afk.on_waiting", ratio=ratio_text))
        else:
            self.afk_status_label.configure(text=t("overlay.afk.on_active", ratio=ratio_text))

        self._refresh_scroll_region()

    def is_afk_enabled(self) -> bool:
        return self._afk_enabled

    def show_scanning(self) -> None:
        self.status_label.configure(text=t("overlay.scanning"))

    def update_wave(self, info: WaveInfo | None, wave: int | None) -> None:
        self._last_wave = info if isinstance(info, WaveInfo) else None
        self._last_wave_num = wave
        if info is None or wave is None:
            self._unrecognized = True
            self.show_waiting(t("overlay.wave_unrecognized"), reset_state=False)
            return

        self._unrecognized = False

        self._enemy_traits = dict(info.enemy_traits or {})
        self.title_label.configure(text=info.mode_name)
        self.wave_label.configure(text=f"Wave {info.wave} / {info.max_wave}")
        if info.game_phase is not None:
            phase_text = (
                info.game_phase.label
                if self.compact
                else f"{info.game_phase.label} — {info.game_phase.tip}"
            )
            self.phase_label.configure(text=phase_text, fg=info.game_phase.color)
        else:
            self.phase_label.configure(text="")
        if info.wave >= info.max_wave and info.final_wave_tip:
            self.status_label.configure(text=info.final_wave_tip, fg="#ffb74d")
        else:
            self.status_label.configure(text="")
        self.danger_label.configure(
            text=t("overlay.danger", text=info.danger_text, score=info.danger_score),
            fg=info.danger_color,
        )
        self.danger_detail_label.configure(text=info.danger_detail)

        self._render_enemy_lines(
            self.enemies_list_frame,
            info.enemies,
            name_color=self.ACCENT,
        )

        if info.skip_at:
            skip_text = t("overlay.skip", time=info.skip_at)
            if info.wave_time:
                skip_text += t("overlay.skip_wave_time", time=info.wave_time)
            self.skip_label.configure(text=skip_text)
        else:
            self.skip_label.configure(text=t("overlay.skip_unknown"))

        self._render_next_wave(info)
        self._scroll_to_top()
        self._refresh_scroll_region()
        self._save_position()

    def destroy(self) -> None:
        self._save_position()
        self.root.destroy()
