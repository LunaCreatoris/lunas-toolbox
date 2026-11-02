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


def test_setup_test_installs_the_pinned_requirements_from_the_folder(monkeypatch):
    calls = []

    def fake_call(command, cwd):
        calls.append((command, cwd))
        return 7

    monkeypatch.setattr(tasks.subprocess, "call", fake_call)
    assert tasks.main(["setup-test"]) == 7
    assert calls == [([tasks.sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], tasks.HERE)]


def test_setup_stays_sdk_only(monkeypatch):
    calls = []

    def fake_call(command, cwd):
        calls.append((command, cwd))
        return 0

    monkeypatch.setattr(tasks.shutil, "which", lambda name: "npm")
    monkeypatch.setattr(tasks.subprocess, "call", fake_call)
    assert tasks.main(["setup"]) == 0
    assert calls == [(["npm", "ci", "--ignore-scripts", "--no-audit", "--no-fund"], tasks.HERE / "sdk")]
