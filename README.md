# Usage gate

Tells an agent factory whether it may start or keep agents running, from the plan usage of your own claude.ai
login. One command, `just usage`, prints the state on its first line and returns it as its exit code.

| State | Exit | When | What the factory does |
|---|---|---|---|
| `go` | 0 | both windows below the caution level | start agents as planned |
| `caution` | 10 | five-hour window at 70% or more | start nothing heavy; let running tasks finish |
| `stop` | 11 | five-hour window at 95% or more | stop running agents cleanly; resume after the reset |
| `weekly` | 12 | seven-day window at 95% or more | stop running agents cleanly; resume after the weekly reset |
| `unknown` | 13 | no reading, or a window missing | at most one agent at a time |

Levels come from `LUNA_USAGE_CAUTION`, `LUNA_USAGE_STOP` and `LUNA_USAGE_WEEKLY_STOP`. A reading younger than
`LUNA_USAGE_CACHE` seconds (60) is reused.

## How it reads the usage

It runs Claude Code's `/usage` command through the official Claude Agent SDK (TypeScript, pinned exactly in
`sdk/package.json`). `/usage` is a local command: no model request is made and no token is spent. The SDK uses
the login Claude Code already has: nothing here reads, copies or stores a credential, and no cookie or
undocumented endpoint is used. Any failure or change in the report's shape reads as `unknown`, never as 0.

**Personal use only.** The Agent SDK documentation says: "Unless previously approved, Anthropic does not allow
third party developers to offer claude.ai login or rate limits for their products, including agents built on the
Claude Agent SDK" ([Agent SDK overview](https://code.claude.com/docs/en/agent-sdk/overview.md)). This tool reads
your own usage, for yourself. Do not offer it to others as a product feature.

## Copy it into another repository

The folder is self-contained: it imports nothing outside itself (a test proves it by copying the folder alone and
running its tests there).

1. Copy the whole `usage/` folder into the repository.
2. Install Python 3.13, Node.js and `just`.
3. In the folder: `just setup` (runs `npm ci` in `sdk/`), then `just usage`.

`just test` runs its tests (pytest, then Node's test runner); pytest is the only Python package they need.

Without `just`: `python3 usage.py` (`py -3.13 usage.py` on Windows), after `npm ci` in `sdk/`. The raw reader is
`node sdk/read_usage.mjs <working folder>`.
