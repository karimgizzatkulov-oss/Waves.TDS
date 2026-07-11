from __future__ import annotations

import ctypes
from ctypes import wintypes
from dataclasses import dataclass
from typing import Any

user32 = ctypes.WinDLL("user32", use_last_error=True)
kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)

GA_ROOT = 2
GWL_EXSTYLE = -20
WS_EX_TOOLWINDOW = 0x00000080
PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
WM_KEYDOWN = 0x0100
WM_KEYUP = 0x0101
MAPVK_VK_TO_VSC = 0

ROBLOX_PROCESS_NAMES = {
    "robloxplayerbeta.exe",
    "robloxplayer.exe",
    "roblox.exe",
}


@dataclass(frozen=True)
class WindowInfo:
    hwnd: int
    title: str
    left: int
    top: int
    width: int
    height: int
    process_name: str = ""

    def label(self) -> str:
        short_title = self.title.strip() or "Без названия"
        if len(short_title) > 36:
            short_title = short_title[:33] + "..."
        process = f" [{self.process_name}]" if self.process_name else ""
        return f"{short_title}{process}  ({self.width}x{self.height})"


class WindowTarget:
    def __init__(self, config: dict[str, Any]) -> None:
        self._config = config
        self._hwnd = int(config.get("window", {}).get("hwnd", 0) or 0)

    @property
    def hwnd(self) -> int:
        return self._hwnd

    @property
    def is_bound(self) -> bool:
        window_cfg = self._config.get("window", {})
        return bool(window_cfg.get("bind")) and self._hwnd > 0

    def update_config(self, config: dict[str, Any]) -> None:
        self._config = config
        self._hwnd = int(config.get("window", {}).get("hwnd", 0) or 0)

    def bind(self, info: WindowInfo) -> None:
        window_cfg = self._config.setdefault("window", {})
        window_cfg["bind"] = True
        window_cfg["hwnd"] = int(info.hwnd)
        window_cfg["title"] = info.title
        self._hwnd = int(info.hwnd)

    def unbind(self) -> None:
        window_cfg = self._config.setdefault("window", {})
        window_cfg["bind"] = False
        window_cfg["hwnd"] = 0
        window_cfg["title"] = ""
        self._hwnd = 0

    def is_valid(self) -> bool:
        if not self.is_bound:
            return False
        return bool(user32.IsWindow(self._hwnd)) and bool(user32.IsWindowVisible(self._hwnd))

    def title(self) -> str:
        return str(self._config.get("window", {}).get("title", ""))

    def client_rect_screen(self) -> dict[str, int] | None:
        if not self.is_valid():
            return None

        rect = wintypes.RECT()
        if not user32.GetClientRect(self._hwnd, ctypes.byref(rect)):
            return None

        point = wintypes.POINT(0, 0)
        if not user32.ClientToScreen(self._hwnd, ctypes.byref(point)):
            return None

        width = int(rect.right - rect.left)
        height = int(rect.bottom - rect.top)
        if width <= 0 or height <= 0:
            return None

        return {
            "left": int(point.x),
            "top": int(point.y),
            "width": width,
            "height": height,
        }

    def region_to_screen(self, region: dict[str, int]) -> dict[str, int] | None:
        client = self.client_rect_screen()
        if client is None:
            return None
        return {
            "left": client["left"] + int(region["left"]),
            "top": client["top"] + int(region["top"]),
            "width": int(region["width"]),
            "height": int(region["height"]),
        }

    def screen_to_region(self, screen_region: dict[str, int]) -> dict[str, int] | None:
        client = self.client_rect_screen()
        if client is None:
            return None
        return {
            "left": int(screen_region["left"]) - client["left"],
            "top": int(screen_region["top"]) - client["top"],
            "width": int(screen_region["width"]),
            "height": int(screen_region["height"]),
        }

    def try_activate(self) -> bool:
        if not self.is_valid():
            return False
        return focus_hwnd(self._hwnd)

    def send_key(self, key: str) -> bool:
        if not self.is_valid():
            return False

        vk = _virtual_key(key)
        if vk is None:
            return False

        scan = user32.MapVirtualKeyW(vk, MAPVK_VK_TO_VSC) & 0xFF
        lparam_down = 1 | (scan << 16)
        lparam_up = 1 | (scan << 16) | (1 << 30) | (1 << 31)
        user32.PostMessageW(self._hwnd, WM_KEYDOWN, vk, lparam_down)
        user32.PostMessageW(self._hwnd, WM_KEYUP, vk, lparam_up)
        return True


def get_foreground_hwnd() -> int:
    return int(user32.GetForegroundWindow())


def focus_hwnd(hwnd: int) -> bool:
    if hwnd <= 0 or not user32.IsWindow(hwnd):
        return False
    if user32.GetForegroundWindow() == hwnd:
        return True

    SW_RESTORE = 9
    user32.ShowWindow(hwnd, SW_RESTORE)

    foreground = user32.GetForegroundWindow()
    foreground_thread = user32.GetWindowThreadProcessId(foreground, None)
    target_thread = user32.GetWindowThreadProcessId(hwnd, None)
    current_thread = kernel32.GetCurrentThreadId()

    attached = False
    if foreground_thread and target_thread and foreground_thread != target_thread:
        attached = bool(user32.AttachThreadInput(current_thread, target_thread, True))
    try:
        return bool(user32.SetForegroundWindow(hwnd))
    finally:
        if attached:
            user32.AttachThreadInput(current_thread, target_thread, False)


def _virtual_key(key: str) -> int | None:
    normalized = key.strip().lower()
    if len(normalized) == 1:
        return ord(normalized.upper())
    aliases = {
        "e": 0x45,
        "space": 0x20,
        "enter": 0x0D,
        "escape": 0x1B,
    }
    return aliases.get(normalized)


def _window_title(hwnd: int) -> str:
    length = user32.GetWindowTextLengthW(hwnd)
    if length <= 0:
        return ""
    buffer = ctypes.create_unicode_buffer(length + 1)
    user32.GetWindowTextW(hwnd, buffer, length + 1)
    return buffer.value


def _window_class(hwnd: int) -> str:
    buffer = ctypes.create_unicode_buffer(256)
    user32.GetClassNameW(hwnd, buffer, 256)
    return buffer.value


def _process_name(hwnd: int) -> str:
    pid = wintypes.DWORD()
    user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
    if not pid.value:
        return ""

    handle = kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, pid.value)
    if not handle:
        return ""

    try:
        buffer = ctypes.create_unicode_buffer(512)
        size = wintypes.DWORD(len(buffer))
        if not kernel32.QueryFullProcessImageNameW(handle, 0, buffer, ctypes.byref(size)):
            return ""
        path = buffer.value.replace("/", "\\")
        return path.rsplit("\\", 1)[-1].lower()
    finally:
        kernel32.CloseHandle(handle)


def _window_rect(hwnd: int) -> tuple[int, int, int, int] | None:
    rect = wintypes.RECT()
    if not user32.GetWindowRect(hwnd, ctypes.byref(rect)):
        return None
    return int(rect.left), int(rect.top), int(rect.right), int(rect.bottom)


def _point_in_rect(x: int, y: int, left: int, top: int, right: int, bottom: int) -> bool:
    return left <= x < right and top <= y < bottom


def _is_roblox_candidate(hwnd: int) -> bool:
    if not user32.IsWindow(hwnd):
        return False
    if not user32.IsWindowVisible(hwnd):
        return False

    ex_style = user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
    if ex_style & WS_EX_TOOLWINDOW:
        return False

    rect = _window_rect(hwnd)
    if rect is None:
        return False
    left, top, right, bottom = rect
    width = right - left
    height = bottom - top
    if width < 200 or height < 150:
        return False

    process_name = _process_name(hwnd)
    if process_name in ROBLOX_PROCESS_NAMES:
        return True

    title = _window_title(hwnd).lower()
    if "roblox" in title:
        return True

    class_name = _window_class(hwnd)
    return class_name in {"WINDOWSCLIENT", "RobloxPlayerBeta"}


def _make_window_info(hwnd: int) -> WindowInfo | None:
    rect = _window_rect(hwnd)
    if rect is None:
        return None
    left, top, right, bottom = rect
    width = right - left
    height = bottom - top
    if width <= 0 or height <= 0:
        return None
    return WindowInfo(
        hwnd=int(hwnd),
        title=_window_title(hwnd),
        left=left,
        top=top,
        width=width,
        height=height,
        process_name=_process_name(hwnd),
    )


def list_roblox_windows() -> list[WindowInfo]:
    results: list[WindowInfo] = []
    seen: set[int] = set()

    def callback(hwnd: int, _lparam: int) -> bool:
        root = user32.GetAncestor(hwnd, GA_ROOT)
        target = int(root or hwnd)
        if target in seen:
            return True
        if not _is_roblox_candidate(target):
            return True
        info = _make_window_info(target)
        if info is None:
            return True
        seen.add(target)
        results.append(info)
        return True

    enum_proc = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)(callback)
    user32.EnumWindows(enum_proc, 0)
    results.sort(key=lambda item: (item.top, item.left))
    return results


def window_at_point(x: int, y: int) -> WindowInfo | None:
    found: list[WindowInfo] = []

    def callback(hwnd: int, _lparam: int) -> bool:
        root = user32.GetAncestor(hwnd, GA_ROOT)
        target = int(root or hwnd)
        if not _is_roblox_candidate(target):
            return True
        rect = _window_rect(target)
        if rect is None:
            return True
        left, top, right, bottom = rect
        if _point_in_rect(x, y, left, top, right, bottom):
            info = _make_window_info(target)
            if info is not None:
                found.append(info)
        return True

    enum_proc = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)(callback)
    user32.EnumWindows(enum_proc, 0)
    if not found:
        return None
    return found[0]


def is_window_binding_enabled(config: dict[str, Any]) -> bool:
    window_cfg = config.get("window", {})
    return bool(window_cfg.get("bind")) and int(window_cfg.get("hwnd", 0) or 0) > 0
