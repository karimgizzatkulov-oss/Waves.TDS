from __future__ import annotations

import tkinter as tk
from tkinter import font as tkfont

from core.i18n import help_sections, t


def populate_help_content(
    content: tk.Frame,
    *,
    bg: str,
    fg: str,
    accent: str,
    scroll_bg: str,
    wrap_width: int,
) -> tk.Label | None:
    for child in content.winfo_children():
        child.destroy()

    title_font = tkfont.Font(family="Segoe UI", size=10, weight="bold")
    body_font = tkfont.Font(family="Segoe UI", size=9)

    title_label = tk.Label(
        content,
        text=t("help.title"),
        bg=bg,
        fg=accent,
        font=tkfont.Font(family="Segoe UI", size=12, weight="bold"),
        anchor="w",
    )
    title_label.pack(fill="x", pady=(0, 8))

    for index, (heading, body) in enumerate(help_sections()):
        tk.Label(
            content,
            text=heading,
            bg=bg,
            fg=fg,
            font=title_font,
            anchor="w",
        ).pack(fill="x", pady=(10 if index else 0, 4))

        tk.Label(
            content,
            text=body,
            bg=scroll_bg,
            fg=fg,
            font=body_font,
            anchor="nw",
            justify="left",
            wraplength=wrap_width,
            padx=8,
            pady=8,
        ).pack(fill="x")

    return title_label


def build_help_panel(
    parent: tk.Misc,
    *,
    bg: str,
    fg: str,
    muted: str,
    accent: str,
    scroll_bg: str,
    wrap_width: int,
) -> tuple[tk.Canvas, tk.Frame]:
    scroll_outer = tk.Frame(parent, bg=bg)
    scroll_outer.pack(fill="both", expand=True)

    canvas = tk.Canvas(scroll_outer, bg=bg, highlightthickness=0, borderwidth=0)
    scrollbar = tk.Scrollbar(
        scroll_outer,
        orient="vertical",
        command=canvas.yview,
        bg="#2a2a44",
        troughcolor=bg,
        activebackground=accent,
    )
    content = tk.Frame(canvas, bg=bg)

    content.bind(
        "<Configure>",
        lambda _event: canvas.configure(scrollregion=canvas.bbox("all")),
    )
    canvas_window = canvas.create_window((0, 0), window=content, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    def on_canvas_configure(event: tk.Event) -> None:
        canvas.itemconfigure(canvas_window, width=event.width)

    canvas.bind("<Configure>", on_canvas_configure)

    populate_help_content(
        content,
        bg=bg,
        fg=fg,
        accent=accent,
        scroll_bg=scroll_bg,
        wrap_width=wrap_width,
    )

    return canvas, content
