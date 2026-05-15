"""Safe computer actions that Frieren can perform.

Only whitelisted operations are allowed. Never executes arbitrary commands.
"""

from __future__ import annotations

import os
import subprocess

EDGE_PATH = "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe"
EDGE_PATH_ALT = "C:\\Program Files\\Microsoft\\Edge\\Application\\msedge.exe"


def _try_start(*commands: str) -> bool:
    """Try each start method, return True if one succeeds."""
    for cmd in commands:
        try:
            subprocess.Popen(
                cmd,
                shell=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            return True
        except Exception:
            continue
    return False


# Map friendly names to launch commands (tried in order)
APP_COMMANDS: dict[str, list[str]] = {
    "qq音乐": [
        'start "" "D:\\software\\QQ音乐\\QQMusic\\QQMusic.exe"',
        'start "" qqmusic://',
        'start "" "QQMusic.exe"',
    ],
    "qqmusic": [
        'start "" "D:\\software\\QQ音乐\\QQMusic\\QQMusic.exe"',
        'start "" qqmusic://',
        'start "" "QQMusic.exe"',
    ],
    "网易云音乐": [
        'start "" orpheus://',
        'start "" "cloudmusic.exe"',
    ],
    "网易云": [
        'start "" orpheus://',
        'start "" "cloudmusic.exe"',
    ],
    "记事本": ['start "" notepad.exe'],
    "计算器": ['start "" calc.exe'],
    "画图": ['start "" mspaint.exe'],
    "任务管理器": ['start "" taskmgr.exe'],
    "资源管理器": ['start "" explorer.exe'],
    "cmd": ['start "" cmd.exe'],
    "终端": ['start "" cmd.exe'],
    "vscode": ['start "" code', 'start "" "Code.exe"'],
    "vs code": ['start "" code', 'start "" "Code.exe"'],
    "浏览器": [f'start "" "{EDGE_PATH}"', f'start "" "{EDGE_PATH_ALT}"'],
    "edge": [f'start "" "{EDGE_PATH}"', f'start "" "{EDGE_PATH_ALT}"'],
}


def open_app(name: str) -> str | None:
    """Open a whitelisted app. Returns error message or None on success."""
    key = name.strip().lower()
    if key not in APP_COMMANDS:
        return f"我不知道怎么打开「{name}」"

    commands = APP_COMMANDS[key]
    if _try_start(*commands):
        return None

    return f"启动「{name}」失败了，它可能没有安装"


def open_url(url: str) -> str | None:
    """Open a URL in Edge browser."""
    if not (url.startswith("http://") or url.startswith("https://")):
        return "只能打开 http/https 链接"

    edge = EDGE_PATH if os.path.exists(EDGE_PATH) else EDGE_PATH_ALT
    if os.path.exists(edge):
        subprocess.Popen(
            [edge, url],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    else:
        os.startfile(url)
    return None


def search_web(query: str) -> str | None:
    """Search the web using Bing."""
    return open_url(f"https://www.bing.com/search?q={query}")
