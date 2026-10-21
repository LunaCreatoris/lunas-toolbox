"""The usage tool's tasks: install the Agent SDK, run the tests. Needs nothing outside this folder."""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def setup() -> int:
    npm = shutil.which("npm")
    if npm is None:
        print("setup: `npm` is not on the PATH: install Node.js first", file=sys.stderr)
        return 1
    return subprocess.call([npm, "ci", "--ignore-scripts", "--no-audit", "--no-fund"], cwd=HERE / "sdk")


def test(extra: list[str]) -> int:
    code = subprocess.call([sys.executable, "-m", "pytest", str(HERE / "tests"), *extra], cwd=HERE)
    node = shutil.which("node")
    if node is None:
        print("test: `node` is not on the PATH, the Node tests cannot run", file=sys.stderr)
        return code or 1
    return code or subprocess.call([node, "--test", *map(str, sorted((HERE / "tests").glob("*.test.mjs")))], cwd=HERE)


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv[:1] == ["setup"]:
        return setup()
    if argv[:1] == ["test"]:
        extra = argv[2:] if argv[1:2] == ["--"] else argv[1:]
        return test(extra)
    print("usage: tasks.py setup | test [-- pytest arguments]", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
