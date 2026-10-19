"""
Unified console entrypoint for experiment CLIs.

Usage::

    uv run experiments screening --list-suites
    uv run experiments screening-loop --loop-mode chunked --chunk-size 10
"""

from __future__ import annotations

import importlib
import sys

COMMANDS: dict[str, tuple[str, str]] = {
    "screening": ("experiments.screening", "main"),
    "screening-loop": ("experiments.screening_loop", "main"),
    "recompute-totals": ("experiments.recompute_totals", "main"),
    "backfill": ("experiments.backfill", "main"),
    "html-report": ("experiments.html_report", "main"),
    "sample-review-suites": ("experiments.sample_review_suites", "main"),
    "plot-leaderboards": ("experiments.plot_screening_leaderboards", "main"),
}


def _usage() -> str:
    lines = [
        "usage: experiments <command> [options]",
        "",
        "Commands:",
    ]
    for name in COMMANDS:
        lines.append(f"  {name}")
    lines.append("")
    lines.append("Run `experiments <command> --help` for command-specific options.")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> None:
    args = list(sys.argv[1:] if argv is None else argv)
    if not args or args[0] in ("-h", "--help"):
        print(_usage())
        return
    command = args[0]
    if command not in COMMANDS:
        print(f"Unknown command: {command}\n", file=sys.stderr)
        print(_usage(), file=sys.stderr)
        sys.exit(2)

    module_name, attr = COMMANDS[command]
    module = importlib.import_module(module_name)
    entry = getattr(module, attr)

    old_argv = sys.argv
    sys.argv = [f"experiments {command}", *args[1:]]
    try:
        entry()
    finally:
        sys.argv = old_argv


if __name__ == "__main__":
    main()
