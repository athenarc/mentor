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
            ["src/mentor/cli.py"],
            {
                "--review-url",
                "--split",
                "--model",
                "--backend",
                "--api-base",
                "--model-profile",
                "--list-reviews",
                "--hide-subagent-steps",
            },
        ),
        (
            ["src/experiments/screening.py", "src/experiments/cli_common.py"],
            {
                "--suite",
                "--reviews",
                "--model-presets",
                "--repeats",
                "--orchestrator-policy",
                "--orchestrator-model",
                "--hide-subagent-steps",
                "--skip-policy-notebook-execution",
                "--skip-totals-aggregation",
                "--canonical",
                "--orchestrator-max-steps",
                "--rerun-in-experiment",
                "--list-suites",
                "--list-model-presets",
                "--list-reviews",
            },
        ),
        (
            ["src/experiments/screening_loop.py", "src/experiments/cli_common.py"],
            {
                "--suite",
                "--reviews",
                "--model-presets",
                "--repeats",
                "--orchestrator-policy",
                "--orchestrator-model",
                "--hide-subagent-steps",
                "--skip-policy-notebook-execution",
                "--skip-totals-aggregation",
                "--canonical",
                "--loop-mode",
                "--chunk-count",
                "--chunk-size",
                "--orchestrator-max-steps",
                "--rerun-in-experiment",
                "--list-suites",
                "--list-model-presets",
                "--list-reviews",
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
