"""The usage tool's own tasks."""

from __future__ import annotations

import tasks


def test_an_unknown_task_prints_its_usage(capsys):
    assert tasks.main(["nope"]) == 2
    assert "setup | test" in capsys.readouterr().err


def test_setup_without_npm_says_what_to_install(monkeypatch, capsys):
    monkeypatch.setattr(tasks.shutil, "which", lambda name: None)
    assert tasks.setup() == 1
    assert "install Node.js" in capsys.readouterr().err
