"""The platform's standard folders: one answer per OS, each tested on every host."""

from __future__ import annotations

import platform_dirs
import pytest


@pytest.mark.parametrize(
    ("platform", "expected"),
    [("darwin", ("Library", "Caches")), ("linux", (".cache",)), ("win32", ("AppData", "Local"))],
)
def test_the_user_cache_folder_follows_the_platform(tmp_path, platform, expected):
    assert platform_dirs.user_cache_dir(platform, {}, tmp_path) == tmp_path.joinpath(*expected)


def test_xdg_cache_home_is_honoured_on_linux(tmp_path):
    env = {"XDG_CACHE_HOME": str(tmp_path / "xdg")}
    assert platform_dirs.user_cache_dir("linux", env, tmp_path) == tmp_path / "xdg"


def test_localappdata_is_honoured_on_windows(tmp_path):
    env = {"LOCALAPPDATA": str(tmp_path / "local")}
    assert platform_dirs.user_cache_dir("win32", env, tmp_path) == tmp_path / "local"
