"""Read the plan usage of the user's claude.ai login and say whether the factory may start agents.

Usage: just usage            (state, both windows, reset times, age of the reading)

The reading comes from the Agent SDK's /usage command, run by `sdk/read_usage.mjs` (Node,
SDK pinned exactly): a local command, so no model request and no token spent (D-013).
A reading younger than LUNA_USAGE_CACHE seconds (60) is reused from the usage file, so a
manager checking before every agent does not start the CLI each time.

The first output line is `state=<state>`, for the manager to gate on; the exit code says
the same:

  0  go         both windows below the caution level
  10 caution    five-hour window >= CAUTION: start nothing heavy, finish running tasks
  11 stop       five-hour window >= STOP: start no agent, report with the reset time
  12 weekly     seven-day window >= WEEKLY_STOP: stop everything but finishing and committing
  13 unknown    no reading (SDK failure, changed report shape, a window missing):
                at most one agent at a time

Levels come from LUNA_USAGE_CAUTION (70), LUNA_USAGE_STOP (95) and LUNA_USAGE_WEEKLY_STOP
(95). A window whose reset time has passed counts as unknown.

Personal use only: this runs the official Agent SDK on the user's own login, and is not
offered to anyone else (see the README and D-013).
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from datetime import datetime
from pathlib import Path

# Self-contained: the only import outside the standard library is this folder's own platform_dirs.py.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from platform_dirs import user_cache_dir

READER = Path(__file__).resolve().parent / "sdk" / "read_usage.mjs"
WINDOWS = ("five_hour", "seven_day")
# The report's meter kinds, as the server names them; rows are classified on `kind` only.
KINDS = {"session": "five_hour", "weekly_all": "seven_day"}
CODES = {"go": 0, "caution": 10, "stop": 11, "weekly": 12, "unknown": 13}
DEFAULTS = {
    "LUNA_USAGE_CAUTION": 70.0,
    "LUNA_USAGE_STOP": 95.0,
    "LUNA_USAGE_WEEKLY_STOP": 95.0,
    "LUNA_USAGE_CACHE": 60.0,
}
ADVICE = {
    "go": "start agents as planned",
    "caution": "start nothing heavy; let the running tasks finish",
    "stop": "start no agent; report to the orchestrator with the reset time",
    "weekly": "stop everything except finishing and committing what is done",
    "unknown": "start at most one agent at a time; tell the user once for this wave",
}
# The first reading after an install starts the SDK cold, which can take over a minute from a network share.
TIMEOUT_S = 180


def levels(env: dict[str, str]) -> dict[str, float]:
    found = {}
    for key, default in DEFAULTS.items():
        try:
            found[key] = float(env.get(key, default))
        except ValueError:
            found[key] = default
    return found


def usage_file(env: dict[str, str]) -> Path:
    if env.get("LUNA_USAGE_FILE"):
        return Path(env["LUNA_USAGE_FILE"])
    return user_cache_dir(env=env) / "luna-usage" / "usage.json"


# ---------------------------------------------------------------------- the report


def epoch(value: object) -> int | None:
    """An ISO 8601 time as Unix seconds, or None."""
    if not isinstance(value, str):
        return None
    try:
        return int(datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp())
    except ValueError:
        return None


def record_from_report(report: object, now: float) -> dict:
    """The usage record of a /usage report: each window, or None when it is missing or malformed."""
    record: dict = dict.fromkeys(WINDOWS)
    limits = (report.get("rate_limits") or {}).get("limits") if isinstance(report, dict) else None
    for row in limits if isinstance(limits, list) else []:
        if not isinstance(row, dict) or row.get("kind") not in KINDS:
            continue
        percent, resets = row.get("percent"), epoch(row.get("resets_at"))
        if isinstance(percent, int | float) and not isinstance(percent, bool) and resets is not None:
            record[KINDS[row["kind"]]] = {"used_percentage": float(percent), "resets_at": resets}
    record["written_at"] = int(now)
    return record


# ------------------------------------------------------------------ reading, cache


def read(path: Path) -> dict | None:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    return data if isinstance(data, dict) else None


def write_atomic(path: Path, record: dict) -> None:
    """Write the reading through a temporary file renamed over it, so a reader never sees half of it."""
    path.parent.mkdir(parents=True, exist_ok=True)
    handle, temporary = tempfile.mkstemp(prefix=".usage-", suffix=".json", dir=path.parent)
    try:
        with os.fdopen(handle, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(record, stream)
            stream.write("\n")
        os.replace(temporary, path)
    except BaseException:
        Path(temporary).unlink(missing_ok=True)
        raise


def run_reader(folder: Path) -> dict:
    """Run the SDK reader; raises RuntimeError with a clear reason when it cannot give a report."""
    node = shutil.which("node")
    if node is None:
        raise RuntimeError("`node` is not on the PATH")
    if not (READER.parent / "node_modules").is_dir():
        raise RuntimeError("the Agent SDK is not installed: run `just setup` in this folder")
    folder.mkdir(parents=True, exist_ok=True)
    try:
        result = subprocess.run(
            [node, str(READER), str(folder)], capture_output=True, text=True, timeout=TIMEOUT_S, cwd=folder
        )
    except subprocess.TimeoutExpired as error:
        raise RuntimeError(f"the SDK gave no answer within {TIMEOUT_S} s") from error
    try:
        answer = json.loads(result.stdout.strip().splitlines()[-1])
    except (IndexError, ValueError) as error:
        raise RuntimeError(f"unreadable SDK answer: {result.stderr.strip()[:200]}") from error
    if answer.get("error"):
        raise RuntimeError(f"SDK error: {answer['error']}")
    if not answer.get("report"):
        raise RuntimeError("the /usage answer carried no usage report (not a claude.ai plan, or its shape changed)")
    return answer


def reading(env: dict[str, str], now: float, fetch=run_reader) -> tuple[dict | None, str]:
    """(record, note): a cached reading younger than the cache window, else a fresh one."""
    path = usage_file(env)
    cached = read(path)
    written = cached.get("written_at") if cached else None
    if isinstance(written, int | float) and 0 <= now - written <= levels(env)["LUNA_USAGE_CACHE"]:
        return cached, "cached"
    try:
        answer = fetch(path.parent)
    except RuntimeError as error:
        return None, str(error)
    record = record_from_report(answer["report"], now)
    write_atomic(path, record)
    cost = answer.get("cost")
    note = "fresh" if cost in (0, None) else f"fresh, but the reading cost {cost} USD (expected 0)"
    return record, note


# ---------------------------------------------------------------------------- state


def live_window(record: dict, name: str, now: float) -> dict | None:
    value = record.get(name)
    if not isinstance(value, dict):
        return None
    if not isinstance(value.get("used_percentage"), int | float) or not isinstance(value.get("resets_at"), int):
        return None
    return value if value["resets_at"] > now else None


def state(record: dict | None, env: dict[str, str], now: float, why_missing: str = "no reading") -> tuple[str, str]:
    """(state, reason) of a reading."""
    limits = levels(env)
    if record is None:
        return "unknown", why_missing
    weekly = live_window(record, "seven_day", now)
    session = live_window(record, "five_hour", now)
    # A known high level stops the line even when the other window is unknown.
    if weekly and weekly["used_percentage"] >= limits["LUNA_USAGE_WEEKLY_STOP"]:
        return "weekly", f"seven-day window at {weekly['used_percentage']:.0f}%"
    if session and session["used_percentage"] >= limits["LUNA_USAGE_STOP"]:
        return "stop", f"five-hour window at {session['used_percentage']:.0f}%"
    if session and session["used_percentage"] >= limits["LUNA_USAGE_CAUTION"]:
        return "caution", f"five-hour window at {session['used_percentage']:.0f}%"
    missing = [name for name, value in (("five-hour", session), ("seven-day", weekly)) if value is None]
    if missing:
        return "unknown", f"{' and '.join(missing)} window unknown"
    return "go", "both windows below the caution level"


def describe(record: dict | None, now: float, note: str) -> list[str]:
    lines = []
    for name, label in zip(WINDOWS, ("five-hour", "seven-day"), strict=True):
        value = live_window(record or {}, name, now)
        if value is None:
            lines.append(f"{label}: unknown")
            continue
        reset = datetime.fromtimestamp(value["resets_at"]).strftime("%Y-%m-%d %H:%M")
        lines.append(f"{label}: {value['used_percentage']:.0f}%, resets {reset} (local time)")
    if record:
        lines.append(f"reading: {note}, {now - record['written_at']:.0f} s old")
    return lines


def main(argv: list[str] | None = None, env: dict[str, str] | None = None, now: float | None = None, fetch=None) -> int:
    env = dict(os.environ) if env is None else env
    now = time.time() if now is None else now
    record, note = reading(env, now, fetch or run_reader)
    current, reason = state(record, env, now, why_missing=note)
    print(f"state={current}")
    print(f"{reason}: {ADVICE[current]}")
    for line in describe(record, now, note):
        print(line)
    return CODES[current]


if __name__ == "__main__":
    sys.exit(main())
