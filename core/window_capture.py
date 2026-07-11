from __future__ import annotations

import ctypes
from ctypes import wintypes

import numpy as np

user32 = ctypes.WinDLL("user32", use_last_error=True)
gdi32 = ctypes.WinDLL("gdi32", use_last_error=True)

SRCCOPY = 0x00CC0020
PW_RENDERFULLCONTENT = 0x00000002
DIB_RGB_COLORS = 0
BI_RGB = 0


class BITMAPINFOHEADER(ctypes.Structure):
    _fields_ = [
        ("biSize", wintypes.DWORD),
        ("biWidth", wintypes.LONG),
        ("biHeight", wintypes.LONG),
        ("biPlanes", wintypes.WORD),
        ("biBitCount", wintypes.WORD),
        ("biCompression", wintypes.DWORD),
        ("biSizeImage", wintypes.DWORD),
        ("biXPelsPerMeter", wintypes.LONG),
        ("biYPelsPerMeter", wintypes.LONG),
        ("biClrUsed", wintypes.DWORD),
        ("biClrImportant", wintypes.DWORD),
    ]


class BITMAPINFO(ctypes.Structure):
    _fields_ = [("bmiHeader", BITMAPINFOHEADER)]


def _bitmap_to_bgr(hdc: int, hbitmap: int, width: int, height: int) -> np.ndarray:
    bmi = BITMAPINFO()
    bmi.bmiHeader.biSize = ctypes.sizeof(BITMAPINFOHEADER)
    bmi.bmiHeader.biWidth = width
    bmi.bmiHeader.biHeight = -height
    bmi.bmiHeader.biPlanes = 1
    bmi.bmiHeader.biBitCount = 32
    bmi.bmiHeader.biCompression = BI_RGB

    buffer_size = width * height * 4
    buffer = ctypes.create_string_buffer(buffer_size)
    lines = gdi32.GetDIBits(
        hdc,
        hbitmap,
        0,
        height,
        buffer,
        ctypes.byref(bmi),
        DIB_RGB_COLORS,
    )
    if lines == 0:
        raise OSError("GetDIBits failed")

    image = np.frombuffer(buffer, dtype=np.uint8).reshape(height, width, 4)
    return image[:, :, :3].copy()


def capture_client_region(hwnd: int, region: dict[str, int]) -> np.ndarray | None:
    left = int(region["left"])
    top = int(region["top"])
    width = int(region["width"])
    height = int(region["height"])
    if width <= 0 or height <= 0 or not user32.IsWindow(hwnd):
        return None

    client = wintypes.RECT()
    if not user32.GetClientRect(hwnd, ctypes.byref(client)):
        return None
    client_w = int(client.right - client.left)
    client_h = int(client.bottom - client.top)
    if client_w <= 0 or client_h <= 0:
        return None

    left = max(0, min(left, client_w - 1))
    top = max(0, min(top, client_h - 1))
    width = min(width, client_w - left)
    height = min(height, client_h - top)
    if width <= 0 or height <= 0:
        return None

    hwnd_dc = user32.GetDC(hwnd)
    if not hwnd_dc:
        return None

    full_dc = gdi32.CreateCompatibleDC(hwnd_dc)
    crop_dc = gdi32.CreateCompatibleDC(hwnd_dc)
    full_bmp = gdi32.CreateCompatibleBitmap(hwnd_dc, client_w, client_h)
    crop_bmp = gdi32.CreateCompatibleBitmap(hwnd_dc, width, height)
    if not full_dc or not crop_dc or not full_bmp or not crop_bmp:
        _release_objects(hwnd, hwnd_dc, full_dc, crop_dc, full_bmp, crop_bmp)
        return None

    try:
        gdi32.SelectObject(full_dc, full_bmp)
        gdi32.SelectObject(crop_dc, crop_bmp)

        printed = user32.PrintWindow(hwnd, full_dc, PW_RENDERFULLCONTENT)
        if not printed:
            gdi32.BitBlt(full_dc, 0, 0, client_w, client_h, hwnd_dc, 0, 0, SRCCOPY)

        gdi32.BitBlt(crop_dc, 0, 0, width, height, full_dc, left, top, SRCCOPY)
        return _bitmap_to_bgr(crop_dc, crop_bmp, width, height)
    except OSError:
        return None
    finally:
        _release_objects(hwnd, hwnd_dc, full_dc, crop_dc, full_bmp, crop_bmp)


def _release_objects(
    hwnd: int,
    hwnd_dc: int,
    full_dc: int,
    crop_dc: int,
    full_bmp: int,
    crop_bmp: int,
) -> None:
    if full_bmp:
        gdi32.DeleteObject(full_bmp)
    if crop_bmp:
        gdi32.DeleteObject(crop_bmp)
    if full_dc:
        gdi32.DeleteDC(full_dc)
    if crop_dc:
        gdi32.DeleteDC(crop_dc)
    if hwnd_dc:
        user32.ReleaseDC(hwnd, hwnd_dc)
