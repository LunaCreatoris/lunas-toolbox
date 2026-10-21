"""The usage gate: the /usage report, the cache, the states and every way a reading goes unknown."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import pytest

import usage

FIXTURE = json.loads((Path(__file__).parent / "fixtures" / "usage_report.json").read_text(encoding="utf-8"))
REPORT = FIXTURE["report"]
NOW = int(datetime.fromisoformat("2030-01-01T01:00:00+00:00").timestamp())


@pytest.fixture
def env(tmp_path):
    return {"LUNA_USAGE_FILE": str(tmp_path / "meter" / "usage.json")}


def fetch_of(report, cost=0, calls=None):
    def fetch(folder):
        if calls is not None:
            calls.append(folder)
        return {"report": report, "cost": cost}

    return fetch


def failing(reason):
    def fetch(folder):
        raise RuntimeError(reason)

    return fetch


def record(five, seven, resets=NOW + 3600, written=NOW):
    def win(value):
        return None if value is None else {"used_percentage": value, "resets_at": resets}

    return {"five_hour": win(five), "seven_day": win(seven), "written_at": written}


# ------------------------------------------------------------------------- report


def test_the_real_report_maps_session_and_weekly_rows():
    data = usage.record_from_report(REPORT, NOW)
    assert data["five_hour"] == {"used_percentage": 53.0, "resets_at": NOW + 4 * 3600}
    assert data["seven_day"]["used_percentage"] == 28.0
    assert data["written_at"] == NOW


def test_rows_are_classified_on_kind_only():
    rows = [{"kind": "weekly_scoped", "group": "weekly", "percent": 99, "resets_at": "2030-01-02T00:00:00Z"}]
    data = usage.record_from_report({"rate_limits": {"limits": rows}}, NOW)
    assert data["five_hour"] is None and data["seven_day"] is None


@pytest.mark.parametrize(
    "report",
    [
        None,
        {},
        {"rate_limits": None},
        {"rate_limits": {"limits": None}},
        {"rate_limits": {"limits": [{"kind": "session", "percent": "53", "resets_at": "2030-01-01T05:00:00Z"}]}},
        {"rate_limits": {"limits": [{"kind": "session", "percent": 53, "resets_at": None}]}},
        {"rate_limits": {"limits": [{"kind": "session", "percent": 53, "resets_at": "tomorrow"}]}},
        {"rate_limits": {"limits": [{"kind": "session", "percent": True, "resets_at": "2030-01-01T05:00:00Z"}]}},
        {"rate_limits": {"limits": ["session"]}},
    ],
)
def test_a_changed_or_missing_shape_is_unknown_never_zero(report):
    data = usage.record_from_report(report, NOW)
    assert data["five_hour"] is None
    assert usage.state(data, {}, NOW)[0] == "unknown"


# ---------------------------------------------------------------------------- cache


def test_a_fresh_reading_is_written_atomically(env, tmp_path):
    data, note = usage.reading(env, NOW, fetch_of(REPORT))
    assert note == "fresh"
    path = usage.usage_file(env)
    assert json.loads(path.read_text(encoding="utf-8")) == data
    assert [p.name for p in path.parent.iterdir()] == ["usage.json"]


def test_a_reading_younger_than_the_cache_window_is_reused(env):
    calls = []
    usage.reading(env, NOW, fetch_of(REPORT, calls=calls))
    _, note = usage.reading(env, NOW + 59, fetch_of(REPORT, calls=calls))
    assert note == "cached"
    assert len(calls) == 1


def test_an_older_reading_is_refreshed(env):
    calls = []
    usage.reading(env, NOW, fetch_of(REPORT, calls=calls))
    usage.reading(env, NOW + 61, fetch_of(REPORT, calls=calls))
    assert len(calls) == 2


def test_the_cache_window_is_configurable(env):
    calls = []
    usage.reading(env, NOW, fetch_of(REPORT, calls=calls))
    usage.reading({**env, "LUNA_USAGE_CACHE": "0"}, NOW + 1, fetch_of(REPORT, calls=calls))
    assert len(calls) == 2


def test_a_reading_from_the_future_is_not_trusted(env):
    usage.write_atomic(usage.usage_file(env), record(10, 10, written=NOW + 600))
    assert usage.reading(env, NOW, fetch_of(REPORT))[1] == "fresh"


def test_a_reading_that_costs_tokens_is_flagged(env):
    _, note = usage.reading(env, NOW, fetch_of(REPORT, cost=0.02))
    assert "cost 0.02 USD" in note


def test_an_sdk_failure_is_unknown_with_its_reason(env, capsys):
    assert usage.main([], env, NOW, failing("SDK error: not logged in")) == usage.CODES["unknown"]
    out = capsys.readouterr().out.splitlines()
    assert out[0] == "state=unknown"
    assert out[1].startswith("SDK error: not logged in")
    assert not usage.usage_file(env).exists()


def test_run_reader_explains_a_missing_node(monkeypatch, tmp_path):
    monkeypatch.setattr(usage.shutil, "which", lambda name: None)
    with pytest.raises(RuntimeError, match="node"):
        usage.run_reader(tmp_path)


# ---------------------------------------------------------------------------- state


@pytest.mark.parametrize(
    ("five", "seven", "expected"),
    [
        (10, 20, "go"),
        (69.9, 20, "go"),
        (70, 20, "caution"),
        (84, 89, "caution"),
        (94, 20, "caution"),
        (95, 20, "stop"),
        (10, 94, "go"),
        (10, 95, "weekly"),
        (90, 96, "weekly"),
        (None, 20, "unknown"),
        (10, None, "unknown"),
        (96, None, "stop"),
        (None, 96, "weekly"),
    ],
)
def test_states_follow_the_default_levels(five, seven, expected):
    assert usage.state(record(five, seven), {}, NOW)[0] == expected


def test_a_window_past_its_reset_is_unknown():
    assert usage.state(record(95, 10, resets=NOW - 1), {}, NOW)[0] == "unknown"


def test_levels_are_configurable_and_bad_values_fall_back():
    env = {"LUNA_USAGE_CAUTION": "50", "LUNA_USAGE_STOP": "x"}
    assert usage.state(record(55, 10), env, NOW)[0] == "caution"
    assert usage.state(record(96, 10), env, NOW)[0] == "stop"


def test_main_prints_the_state_first_and_exits_with_its_code(env, capsys):
    report = json.loads(json.dumps(REPORT))
    report["rate_limits"]["limits"][0]["percent"] = 96
    assert usage.main([], env, NOW, fetch_of(report)) == usage.CODES["stop"]
    lines = capsys.readouterr().out.splitlines()
    assert lines[0] == "state=stop"
    assert "start no agent" in lines[1]
    assert lines[2].startswith("five-hour: 96%, resets ")
    assert lines[-1].startswith("reading: fresh, 0 s old")


def test_the_real_fixture_reads_as_go(env):
    assert usage.main([], env, NOW, fetch_of(REPORT)) == usage.CODES["go"]
