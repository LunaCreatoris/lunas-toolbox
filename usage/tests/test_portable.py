"""The folder is self-contained: copied anywhere on its own, its code imports nothing outside it and its tests pass."""

from __future__ import annotations

import ast
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parents[1]
# Set in the copy's environment, so the copy does not copy itself again.
NESTED = "USAGE_PORTABILITY_COPY"


def local_modules() -> set[str]:
    return {path.stem for path in HERE.glob("*.py")}


def imported_modules(path: Path) -> set[str]:
    names = set()
    for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
        if isinstance(node, ast.Import):
            names.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            names.add(node.module.split(".")[0])
    return names


def test_every_import_is_the_standard_library_or_this_folder():
    allowed = set(sys.stdlib_module_names) | local_modules() | {"pytest", "__future__"}
    for path in [*HERE.glob("*.py"), *HERE.glob("tests/*.py")]:
        outside = imported_modules(path) - allowed
        assert outside == set(), f"{path.name} imports {sorted(outside)} from outside the folder"


@pytest.mark.skipif(os.environ.get(NESTED) == "1", reason="already running inside the portability copy")
def test_a_copy_of_the_folder_alone_passes_its_own_tests(tmp_path):
    copy = tmp_path / "usage"
    shutil.copytree(HERE, copy, ignore=shutil.ignore_patterns("node_modules", "__pycache__", ".pytest_cache"))
    env = {key: value for key, value in os.environ.items() if key not in ("PYTHONPATH",)}
    env[NESTED] = "1"
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "tests", "-q"], cwd=copy, env=env, capture_output=True, text=True
    )
    assert result.returncode == 0, result.stdout + result.stderr
    node = shutil.which("node")
    if node is not None:
        tests = [str(p) for p in sorted((copy / "tests").glob("*.test.mjs"))]
        result = subprocess.run([node, "--test", *tests], cwd=copy, capture_output=True, text=True)
        assert result.returncode == 0, result.stdout + result.stderr
