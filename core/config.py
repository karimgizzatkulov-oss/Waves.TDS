from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CONFIG: dict[str, Any] = {
    "mode": "hardcore",
    "language": "ru",
    "ocr_region": {
        "left": 690,
        "top": 22,
        "width": 155,
        "height": 65,
    },
    "overlay": {
        "x": 1600,
        "y": 50,
        "opacity": 0.85,
        "compact": False,
        "follow_window": True,
        "window_offset_x": 0,
        "window_offset_y": 0,
    },
    "window": {
        "bind": False,
        "hwnd": 0,
        "title": "",
    },
    "ocr": {
        "poll_ms": 50,
        "stable_frames": 3,
    },
    "afk": {
        "pump_region": {
            "left": 0,
            "top": 0,
            "width": 0,
            "height": 0,
        },
        "poll_ms": 150,
        "cooldown_ms": 500,
        "ready_frames": 2,
        "green_ratio_threshold": 0.12,
        "hotkey": "f8",
        "pump_burst_max": 8,
        "pump_repeat_delay_ms": 120,
    },
}


def config_path() -> Path:
    return ROOT / "config.json"


def load_config() -> dict[str, Any]:
    path = config_path()
    if not path.exists():
        return deepcopy(DEFAULT_CONFIG)

    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)

    merged = deepcopy(DEFAULT_CONFIG)
    merged.update({key: value for key, value in data.items() if key in merged})
    for section in ("ocr_region", "overlay", "ocr", "afk", "window"):
        if section in data and isinstance(data[section], dict):
            merged[section].update(data[section])
    if "afk" in data and isinstance(data["afk"], dict):
        pump_region = data["afk"].get("pump_region")
        if isinstance(pump_region, dict):
            merged["afk"]["pump_region"].update(pump_region)
    return merged


def is_pump_region_configured(config: dict) -> bool:
    region = config.get("afk", {}).get("pump_region", {})
    return int(region.get("width", 0)) > 0 and int(region.get("height", 0)) > 0


def save_config(config: dict[str, Any]) -> None:
    path = config_path()
    with path.open("w", encoding="utf-8") as handle:
        json.dump(config, handle, indent=2, ensure_ascii=False)
        handle.write("\n")
