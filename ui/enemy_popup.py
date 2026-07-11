from __future__ import annotations

import tkinter as tk
from tkinter import font as tkfont

from core.enemy_info import format_enemy_details
from core.wave_data import EnemyLine

_active_popup: tk.Toplevel | None = None


def close_enemy_popup() -> None:
    global _active_popup
    if _active_popup is not None:
        try:
            _active_popup.destroy()
        except tk.TclError:
            pass
        _active_popup = None


def show_enemy_popup(
    parent: tk.Misc,
    enemy: EnemyLine,
    enemy_traits: dict[str, list[str]],
) -> None:
    close_enemy_popup()

    popup = tk.Toplevel(parent)
    popup.title(enemy.type)
    popup.configure(bg="#1a1a2e")
    popup.resizable(False, False)
    popup.attributes("-topmost", True)

    title_font = tkfont.Font(family="Segoe UI", size=11, weight="bold")
    body_font = tkfont.Font(family="Segoe UI", size=9)

    header = tk.Frame(popup, bg="#1a1a2e", padx=12, pady=8)
    header.pack(fill="x")

    tk.Label(
        header,
        text=enemy.type,
        bg="#1a1a2e",
        fg="#7c9cff",
        font=title_font,
        anchor="w",
    ).pack(side="left", fill="x", expand=True)

    close_label = tk.Label(
        header,
        text="×",
        bg="#1a1a2e",
        fg="#9aa0b5",
        font=title_font,
        cursor="hand2",
    )
    close_label.pack(side="right")
    close_label.bind("<Button-1>", lambda _event: close_enemy_popup())

    body = format_enemy_details(enemy, enemy_traits)
    tk.Label(
        popup,
        text=body,
        bg="#121223",
        fg="#eaeaea",
        font=body_font,
        justify="left",
        anchor="nw",
        padx=12,
        pady=10,
        wraplength=280,
    ).pack(fill="both", padx=12, pady=(0, 12))

    popup.update_idletasks()
    width = max(popup.winfo_reqwidth(), 260)
    height = popup.winfo_reqheight()

    parent.update_idletasks()
    px = parent.winfo_rootx() + max(0, parent.winfo_width() - width - 8)
    py = parent.winfo_rooty() + 48
    screen_w = popup.winfo_screenwidth()
    screen_h = popup.winfo_screenheight()
    px = min(max(8, px), max(8, screen_w - width - 8))
    py = min(max(8, py), max(8, screen_h - height - 8))
    popup.geometry(f"{width}x{height}+{px}+{py}")

    popup.bind("<Escape>", lambda _event: close_enemy_popup())
    popup.protocol("WM_DELETE_WINDOW", close_enemy_popup)

    global _active_popup
    _active_popup = popup
