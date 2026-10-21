"""The justfile's shell: runs a recipe line without any system shell (`set shell`).

just runs `<python> recipe_shell.py "<line>" <recipe> [arguments...]`: positional
arguments are on, so the recipe's arguments follow its name as separate argv entries.
No shell ever re-parses them, so `just guards-install "My Project"` reaches the script
as one argument, spaces, quotes and `$` included, the same under sh, PowerShell or
cmd. sh and PowerShell would have re-split or joined them.

<python> is `py -3.13` on Windows (the python.org launcher: the `python` on the PATH may
be another version or the Store stub) and `python3` elsewhere. This file checks it is at
least 3.13, then runs the line: words split POSIX-style, a line that starts with a `.py`
script runs with this same interpreter, anything else (`just --list`) runs as a program.
For a script, the full command (script and arguments) is echoed to stderr first: every
recipe line starts with `@`, so just echoes nothing and this is the only echo.

This file must stay importable by an older Python, so that the version check can speak.
"""

from __future__ import annotations

import shlex
import subprocess
import sys

MINIMUM_VERSION = (3, 13)


def check_version(version: tuple[int, ...] | None = None) -> None:
    """Stop with a clear message on a Python older than 3.13."""
    version = tuple(sys.version_info if version is None else version)
    if version[:2] < MINIMUM_VERSION:
        raise SystemExit(
            f"recipe_shell.py: the recipes need Python {MINIMUM_VERSION[0]}.{MINIMUM_VERSION[1]} or newer,"
            f" but `just` started Python {version[0]}.{version[1]}. Install Python 3.13 (on Windows, from"
            " python.org, with the `py` launcher), then try again."
        )


def recipe_words(argv: list[str]) -> list[str]:
    """The words a recipe runs, before the interpreter: `argv` is [line, recipe name, arguments...]."""
    if not argv or not argv[0].strip():
        raise SystemExit("recipe_shell.py: no recipe line to run")
    return [*shlex.split(argv[0]), *argv[2:]]


def command(argv: list[str]) -> list[str]:
    """The command of a recipe line: a `.py` script runs with the interpreter running this file."""
    words = recipe_words(argv)
    if words[0].endswith(".py"):
        words = [sys.executable, *words]
    return words


def exit_code(code: int) -> int:
    """A child killed by a signal has a negative code: report it as a shell does, 128 + signal."""
    return 128 - code if code < 0 else code


def main(argv: list[str] | None = None) -> int:
    check_version()
    argv = list(sys.argv[1:] if argv is None else argv)
    words = recipe_words(argv)
    to_run = command(argv)
    if words[0].endswith(".py"):
        print(f"$ {shlex.join(words)}", file=sys.stderr, flush=True)
    try:
        process = subprocess.Popen(to_run)
    except FileNotFoundError:
        print(f"recipe_shell.py: {to_run[0]} not found", file=sys.stderr)
        return 127
    while True:
        try:
            return exit_code(process.wait())
        except KeyboardInterrupt:
            # Ctrl-C reached the child too: let it stop on its own terms, and return its code.
            continue


if __name__ == "__main__":
    sys.exit(main())
