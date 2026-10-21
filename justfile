# The usage gate, a self-contained tool: copy this folder into any repository and run `just setup` once.
#
# Recipes only call Python scripts of this folder, through recipe_shell.py (a copy of the ToolBox's recipe shell,
# so the folder needs nothing outside it): arguments reach the scripts intact on every OS.

set positional-arguments
set windows-shell := ["py", "-3.13", "recipe_shell.py"]
set shell := ["python3", "recipe_shell.py"]

# List every recipe
default:
    @just --list --unsorted

# Plan usage of your claude.ai login via the Agent SDK, zero tokens: state, windows, reset times (exit code = state)
usage:
    @usage.py

# Install the Agent SDK (pinned) with npm; needs Node.js
setup:
    @tasks.py setup

# Run this folder's tests (pytest, then Node's test runner)
test *ARGS:
    @tasks.py test

# The folder's gate: its tests (the root gate calls this)
ci:
    @tasks.py test
