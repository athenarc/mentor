"""CLI for ``experiments suite``: expand review×profile×repeat grid and run Mentor."""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from dotenv import load_dotenv

from experiments.suites.review_suites import list_review_suites
from experiments.suites.runner import run_suite
from experiments.catalog import list_model_profiles, list_models

logger = logging.getLogger(__name__)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="experiments suite",
        description=(
            "Run a Mentor suite grid (reviews × profiles × repeats). "
            "Loads Cochrane reviews, writes review.json per cell, and calls Mentor."
        ),
    )
    parser.add_argument(
        "--suite",
        default="screening_ladder",
        help="Canonical suite name from experiments/config/suites.json.",
    )
    parser.add_argument(
        "--reviews",
        nargs="+",
        default=None,
        help="Optional subset of suite review keys (Cochrane URLs).",
    )
    parser.add_argument(
        "--profiles",
        nargs="+",
        default=None,
        help="Override suite run.profiles (profile keys from model_profiles.json).",
    )
    parser.add_argument(
        "--repeats",
        type=int,
        default=None,
        help="Override suite run.repeats.",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Override suite run.batch_size (omit for suite default; pass explicitly for None).",
    )
    parser.add_argument(
        "--stages",
        choices=["full", "screening-only", "screening"],
        default=None,
        help="Override suite run.stages (default: suite or screening-only).",
    )
    parser.add_argument(
        "--resume",
        type=Path,
        default=None,
        help="Resume an existing experiment directory (skip completed runs).",
    )
    parser.add_argument(
        "--hide-subagent-steps",
        action="store_true",
        help="Hide managed-agent steps from console and agent.log.",
    )
    parser.add_argument(
        "--list-suites",
        action="store_true",
        help="List available suites and exit.",
    )
    parser.add_argument(
        "--list-profiles",
        action="store_true",
        help="List available model profiles and exit.",
    )
    parser.add_argument(
        "--list-models",
        action="store_true",
        help="List model catalogue keys and exit.",
    )
    return parser


def main(argv: list[str] | None = None) -> None:
    load_dotenv(override=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )

    raw = list(sys.argv[1:] if argv is None else argv)
    batch_size_set = "--batch-size" in raw
    args = _build_parser().parse_args(raw)

    if args.list_suites:
        for name in list_review_suites():
            print(f"  {name}")
        return
    if args.list_profiles:
        for key in list_model_profiles():
            print(f"  {key}")
        return
    if args.list_models:
        for key in list_models():
            print(f"  {key}")
        return

    try:
        experiment_dir = run_suite(
            suite_name=args.suite,
            review_keys=args.reviews,
            profiles=args.profiles,
            repeats=args.repeats,
            batch_size=args.batch_size,
            stages=args.stages,
            include_subagent_steps=not args.hide_subagent_steps,
            resume_dir=args.resume,
            batch_size_set=batch_size_set,
        )
    except ValueError as exc:
        logger.error("%s", exc)
        sys.exit(1)

    logger.info("Experiment directory: %s", experiment_dir)
    print(experiment_dir)


if __name__ == "__main__":
    main()
