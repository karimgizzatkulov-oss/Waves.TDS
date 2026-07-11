from __future__ import annotations

from typing import Any

from core.window_target import WindowTarget, is_window_binding_enabled


def stored_region_to_screen(config: dict[str, Any], region: dict[str, int]) -> dict[str, int] | None:
    if is_window_binding_enabled(config):
        return WindowTarget(config).region_to_screen(region)
    return dict(region)


def screen_region_to_stored(config: dict[str, Any], screen_region: dict[str, int]) -> dict[str, int] | None:
    if is_window_binding_enabled(config):
        return WindowTarget(config).screen_to_region(screen_region)
    return dict(screen_region)
