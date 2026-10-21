"""The platform's standard folders, for files the tooling keeps per user (OS-specific by nature)."""

from __future__ import annotations

import os
import sys
from pathlib import Path


def user_cache_dir(platform: str = sys.platform, env: dict[str, str] | None = None, home: Path | None = None) -> Path:
    """The per-user cache folder: `~/Library/Caches` on macOS, `%LOCALAPPDATA%` on Windows, XDG elsewhere."""
    env = dict(os.environ) if env is None else env
    home = Path.home() if home is None else home
    if platform == "win32":
        local = env.get("LOCALAPPDATA")
        return Path(local) if local else home / "AppData" / "Local"
    if platform == "darwin":
        return home / "Library" / "Caches"
    xdg = env.get("XDG_CACHE_HOME")
    return Path(xdg) if xdg else home / ".cache"
