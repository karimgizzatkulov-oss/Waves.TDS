from __future__ import annotations

import tkinter as tk
from tkinter import font as tkfont
from tkinter import messagebox
from typing import Callable

from core.window_target import WindowInfo, list_roblox_windows, window_at_point


class WindowSelectDialog:
    BG = "#1a1a2e"
    FG = "#eaeaea"
    MUTED = "#9aa0b5"
    ACCENT = "#7c9cff"

    def __init__(
        self,
        parent: tk.Misc,
        on_done: Callable[[WindowInfo | None | bool], None],
        allow_unbind: bool = True,
    ) -> None:
        self.parent = parent
        self.on_done = on_done
        self.allow_unbind = allow_unbind
        self._pick_mode = False
        self._pick_window: tk.Toplevel | None = None
        self._pick_hint: tk.Toplevel | None = None
        self._items: list[WindowInfo] = []

        self.root = tk.Toplevel(parent)
        self.root.title("Выбор окна Roblox")
        self.root.configure(bg=self.BG)
        self.root.resizable(True, True)
        self.root.minsize(640, 460)
        self.root.attributes("-topmost", True)
        self._build_ui()
        self._show_centered()
        self.root.grab_set()
        self.root.focus_force()
        self.root.protocol("WM_DELETE_WINDOW", self._cancel)

    def _build_ui(self) -> None:
        title_font = tkfont.Font(family="Segoe UI", size=13, weight="bold")
        body_font = tkfont.Font(family="Segoe UI", size=10)
        button_font = tkfont.Font(family="Segoe UI", size=10, weight="bold")

        frame = tk.Frame(self.root, bg=self.BG, padx=20, pady=18)
        frame.pack(fill="both", expand=True)

        tk.Label(
            frame,
            text="Привязать хелпер к окну Roblox",
            bg=self.BG,
            fg=self.FG,
            font=title_font,
            anchor="w",
        ).pack(fill="x")

        tk.Label(
            frame,
            text=(
                "OCR, Pump и AFK будут работать только с выбранным окном.\n"
                "RAM / Roblox Account Manager поддерживается.\n"
                "Если в списке пусто — нажми «Обновить» или «Кликнуть по окну»."
            ),
            bg=self.BG,
            fg=self.MUTED,
            font=body_font,
            justify="left",
        ).pack(fill="x", pady=(8, 12))

        list_frame = tk.Frame(frame, bg="#121223")
        list_frame.pack(fill="both", expand=True)

        self.listbox = tk.Listbox(
            list_frame,
            width=62,
            height=8,
            bg="#121223",
            fg=self.FG,
            selectbackground=self.ACCENT,
            selectforeground="#1a1a2e",
            font=body_font,
            relief="flat",
            highlightthickness=0,
            activestyle="none",
        )
        self.listbox.pack(fill="both", expand=True, padx=8, pady=8)
        self.listbox.bind("<Double-Button-1>", lambda _event: self._accept_selection())

        self.status_label = tk.Label(
            frame,
            text="",
            bg=self.BG,
            fg="#ff8a80",
            font=body_font,
            anchor="w",
            wraplength=580,
            justify="left",
        )
        self.status_label.pack(fill="x", pady=(6, 0))

        self._refresh_list()

        button_row = tk.Frame(frame, bg=self.BG)
        button_row.pack(fill="x", pady=(14, 0))

        tk.Button(
            button_row,
            text="Обновить",
            command=self._refresh_list,
            font=body_font,
            padx=10,
            pady=4,
        ).pack(side="left")

        tk.Button(
            button_row,
            text="Кликнуть по окну",
            command=self._start_pick_mode,
            font=body_font,
            padx=10,
            pady=4,
        ).pack(side="left", padx=(8, 0))

        tk.Button(
            button_row,
            text="Выбрать",
            command=self._accept_selection,
            font=button_font,
            padx=12,
            pady=4,
        ).pack(side="right")

        if self.allow_unbind:
            tk.Button(
                button_row,
                text="Без привязки",
                command=self._choose_unbound,
                font=body_font,
                padx=10,
                pady=4,
            ).pack(side="right", padx=(0, 8))

        tk.Button(
            button_row,
            text="Отмена",
            command=self._cancel,
            font=body_font,
            padx=10,
            pady=4,
        ).pack(side="right", padx=(0, 8))

    def _refresh_list(self) -> None:
        self._items = list_roblox_windows()
        self.listbox.delete(0, "end")
        self.status_label.configure(text="")
        if not self._items:
            self.listbox.insert(
                "end",
                "Окна Roblox не найдены — открой игру через RAM и нажми «Обновить»",
            )
            self.status_label.configure(
                text=(
                    "Найдено окон: 0. Подсказка: в RAM окно часто называется именем игры, "
                    "не «Roblox». Игра должна быть развёрнута, не свёрнута."
                )
            )
            return
        for item in self._items:
            self.listbox.insert("end", item.label())
        self.listbox.selection_set(0)
        self.status_label.configure(
            text=f"Найдено окон Roblox: {len(self._items)}. Выбери нужное и нажми «Выбрать».",
            fg="#9ad09a",
        )

    def _accept_selection(self) -> None:
        if not self._items:
            messagebox.showwarning(
                "Окна не найдены",
                "Сначала открой Roblox (через RAM тоже можно), затем нажми «Обновить».",
                parent=self.root,
            )
            return
        selection = self.listbox.curselection()
        if not selection:
            messagebox.showinfo(
                "Выбери окно",
                "Кликни по строке в списке или используй «Кликнуть по окну».",
                parent=self.root,
            )
            return
        self._finish(self._items[int(selection[0])])

    def _choose_unbound(self) -> None:
        self._finish(None)

    def _start_pick_mode(self) -> None:
        self._pick_mode = True
        self.root.withdraw()
        self.root.grab_release()

        self._pick_window = tk.Toplevel(self.parent)
        self._pick_window.attributes("-fullscreen", True)
        self._pick_window.attributes("-topmost", True)
        self._pick_window.attributes("-alpha", 0.01)
        self._pick_window.configure(bg="black", cursor="crosshair")
        self._pick_window.bind("<ButtonRelease-1>", self._on_pick_click)
        self._pick_window.bind("<Escape>", lambda _event: self._cancel_pick_mode())

        self._pick_hint = tk.Toplevel(self.parent)
        self._pick_hint.overrideredirect(True)
        self._pick_hint.attributes("-topmost", True)
        self._pick_hint.configure(bg="#1a1a2e")
        tk.Label(
            self._pick_hint,
            text="Отпусти кнопку мыши над нужным окном Roblox  |  Esc — отмена",
            bg="#1a1a2e",
            fg="#eaeaea",
            font=tkfont.Font(family="Segoe UI", size=11),
            padx=16,
            pady=12,
        ).pack()
        self._pick_hint.update_idletasks()
        self._pick_hint.geometry(f"520x56+{self._pick_hint.winfo_screenwidth() // 2 - 260}+24")

    def _on_pick_click(self, event: tk.Event) -> None:
        if not self._pick_mode:
            return
        info = window_at_point(event.x_root, event.y_root)
        self._close_pick_mode()
        if info is None:
            self.root.deiconify()
            self.root.grab_set()
            messagebox.showwarning(
                "Окно не распознано",
                "Под курсором не найден Roblox.\n"
                "Попробуй кликнуть по центру игры или выбери из списка после «Обновить».",
                parent=self.root,
            )
            return
        self._finish(info)

    def _cancel_pick_mode(self) -> None:
        self._close_pick_mode()
        self.root.deiconify()
        self.root.grab_set()

    def _close_pick_mode(self) -> None:
        self._pick_mode = False
        if self._pick_hint is not None:
            self._pick_hint.destroy()
            self._pick_hint = None
        if self._pick_window is not None:
            self._pick_window.destroy()
            self._pick_window = None

    def _finish(self, info: WindowInfo | None) -> None:
        self._close_pick_mode()
        try:
            self.root.grab_release()
        except tk.TclError:
            pass
        self.root.destroy()
        self.on_done(info)

    def _cancel(self) -> None:
        self._close_pick_mode()
        try:
            self.root.grab_release()
        except tk.TclError:
            pass
        self.root.destroy()
        self.on_done(False)

    def _show_centered(self) -> None:
        width = 640
        height = 460
        self.root.update_idletasks()
        x = max(0, self.root.winfo_screenwidth() // 2 - width // 2)
        y = max(0, self.root.winfo_screenheight() // 2 - height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")
        self.root.lift()
        self.root.attributes("-topmost", True)

    def run(self) -> None:
        self.parent.wait_window(self.root)


def ask_window_target(parent: tk.Misc, allow_unbind: bool = True) -> WindowInfo | None | bool:
    result: dict[str, WindowInfo | None | bool] = {"value": False}

    def on_done(value: WindowInfo | None | bool) -> None:
        result["value"] = value

    dialog = WindowSelectDialog(parent=parent, on_done=on_done, allow_unbind=allow_unbind)
    dialog.run()
    return result["value"]
