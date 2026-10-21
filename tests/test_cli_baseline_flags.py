"""CLI flag surface regression tests (module paths post-restructure)."""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def _add_argument_flags(path: Path) -> list[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    flags: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and getattr(node.func, "attr", None) == "add_argument":
            if node.args and isinstance(node.args[0], ast.Constant):
                flags.append(node.args[0].value)
    return flags


@pytest.mark.parametrize(
    ("relpaths", "expected"),
    [
        (
            ["src/cli.py"],
            {
                "--review",
                "--model",
                "--backend",
                "--api-base",
                "--profile",
                "--batch-size",
                "--output-root",
                "--run-name",
                "--hide-subagent-steps",
                "--list-profiles",
            },
        ),
        (
            ["experiments/suite_cli.py"],
            {
                "--suite",
                "--reviews",
                "--profiles",
                "--repeats",
                "--batch-size",
                "--stages",
                "--resume",
                "--hide-subagent-steps",
                "--list-suites",
                "--list-profiles",
                "--list-models",
            },
        ),
        (
            ["experiments/analyze.py"],
            {
                "--label-policies",
                "--execute-notebooks",
                "--skip-totals",
            },
        ),
    ],
)
def test_cli_flags_preserved(relpaths: list[str], expected: set[str]) -> None:
    flags: set[str] = set()
    for relpath in relpaths:
        path = ROOT / relpath
        if not path.exists():
            pytest.skip(f"{relpath} not created yet")
        flags |= set(_add_argument_flags(path))
    missing = expected - flags
    assert not missing, f"Missing flags in {relpaths}: {sorted(missing)}"
