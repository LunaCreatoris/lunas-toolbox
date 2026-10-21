# Changelog

Rules of this file:

- Every change gets one line, in English, written for someone reading the history: what changed, not how.
- Newest first, under a period heading (`## YYYY-MM`).
- Breaking changes, removals and migrations start with **Breaking**, **Removed** or **Migration**, and say what the
  reader has to do.

## 2026-10

- The usage gate stands alone: its own licence, README, changelog and git files, so the folder can be copied or
  published by itself.
- **Migration**: the files moved from `tools/usage.py`, `tools/platform_dirs.py` and `tools/usage-sdk/` into this
  folder (`usage.py`, `platform_dirs.py`, `sdk/`); replace any copy taken from the old paths with the whole folder.
- At 95% of either window the gate says to stop running agents cleanly and names the reset after which work
  resumes; caution stays at 70% of the five-hour window.
- `just usage` reads the plan usage on demand through the Agent SDK's `/usage` command, at no token cost, cached
  for a minute, and prints `state=go|caution|stop|weekly|unknown` with the matching exit code.
