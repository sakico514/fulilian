"""Get current Windows desktop context: active window, nearby windows."""

from __future__ import annotations

import ctypes
from ctypes import wintypes

user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32
psapi = ctypes.windll.psapi


def get_active_window_title() -> str:
    hwnd = user32.GetForegroundWindow()
    length = user32.GetWindowTextLengthW(hwnd)
    buf = ctypes.create_unicode_buffer(length + 1)
    user32.GetWindowTextW(hwnd, buf, length + 1)
    return buf.value


def get_active_process_name() -> str:
    hwnd = user32.GetForegroundWindow()
    pid = wintypes.DWORD()
    user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
    handle = kernel32.OpenProcess(0x0400 | 0x0010, False, pid)
    if not handle:
        return ""
    buf = ctypes.create_unicode_buffer(260)
    size = wintypes.DWORD(260)
    psapi.GetModuleBaseNameW(handle, None, buf, size)
    kernel32.CloseHandle(handle)
    return buf.value


def get_nearest_window(pet_x: int, pet_y: int, pet_w: int, pet_h: int) -> str:
    """Find the visible window closest to the pet's position.
    Returns the window title, or empty string if nothing nearby."""
    pet_cx = pet_x + pet_w // 2
    pet_cy = pet_y + pet_h // 2

    results = []
    WNDENUMPROC = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)

    def enum_callback(hwnd, _lparam):
        if not user32.IsWindowVisible(hwnd):
            return True
        # Skip tiny windows and tool windows
        rect = wintypes.RECT()
        user32.GetWindowRect(hwnd, ctypes.byref(rect))
        w = rect.right - rect.left
        h = rect.bottom - rect.top
        if w < 200 or h < 100:
            return True
        # Skip the pet's own window and other transparent/tool windows
        style = user32.GetWindowLongW(hwnd, -16)  # GWL_STYLE
        if not (style & 0x00C00000):  # Skip windows without caption
            return True

        length = user32.GetWindowTextLengthW(hwnd)
        if length == 0:
            return True
        buf = ctypes.create_unicode_buffer(length + 1)
        user32.GetWindowTextW(hwnd, buf, length + 1)
        title = buf.value
        if not title:
            return True

        # Distance from pet center to window rect
        cx = (rect.left + rect.right) // 2
        cy = (rect.top + rect.bottom) // 2
        dist = ((pet_cx - cx) ** 2 + (pet_cy - cy) ** 2) ** 0.5
        results.append((dist, title))
        return True

    callback = WNDENUMPROC(enum_callback)
    user32.EnumWindows(callback, 0)

    if not results:
        return ""

    results.sort(key=lambda r: r[0])
    return results[0][1]


def get_nearby_context(pet_x: int, pet_y: int, pet_w: int, pet_h: int) -> str:
    """Get the window that the pet is placed near/on."""
    nearby = get_nearest_window(pet_x, pet_y, pet_w, pet_h)
    if nearby:
        return f"芙莉莲正站在「{nearby}」窗口旁边"
    return ""


def get_desktop_context(
    pet_x: int = 0, pet_y: int = 0, pet_w: int = 0, pet_h: int = 0
) -> str:
    parts = []
    active = get_active_window_title()
    proc = get_active_process_name()
    if active:
        parts.append(f"主人当前活跃窗口: {active} ({proc})" if proc else f"主人活跃窗口: {active}")

    if pet_w > 0 and pet_h > 0:
        nearby = get_nearby_context(pet_x, pet_y, pet_w, pet_h)
        if nearby and nearby.split("「")[1].split("」")[0] != active:
            parts.append(nearby)

    return "。".join(parts) if parts else ""
