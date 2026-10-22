"""Mentor CLI: run one systematic review from a JSON file."""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from dotenv import load_dotenv

from mentor.runtime.models import (
    has_explicit_model_config,
    resolve_api_base,
    resolve_backend,
    resolve_model_id,
)
from mentor.runtime.profile_resolver import (
    get_selected_model_profile,
    list_model_profiles,
)
from mentor.runtime.run import run_review

logger = logging.getLogger(__name__)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="mentor",
        description="Run Mentor on one systematic review JSON file.",
    )
    parser.add_argument(
        "--review",
        default=None,
        help="Path to a review JSON file (mode, protocol fields, optional studies).",
    )
    parser.add_argument(
        "--profile",
        dest="model_profile",
        default=None,
        help=(
            "Named model profile from mentor/config/model_profiles.json "
            "(cannot combine with --model/--backend/--api-base)."
        ),
    )
    parser.add_argument(
        "--list-profiles",
        action="store_true",
        help="List available model profiles and exit.",
    )
    parser.add_argument(
        "--model",
        default=None,
        help="Override model id (default: MENTOR_MODEL / gpt-4.1).",
    )
    parser.add_argument(
        "--backend",
        choices=["openai", "transformers"],
        default=None,
        help="Model backend (default: MENTOR_BACKEND / openai).",
    )
    parser.add_argument(
        "--api-base",
        default=None,
        help="Override OpenAI-compatible API base URL.",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Screening batch size (omit for single-pass screening).",
    )
    parser.add_argument(
        "--output-root",
        default=None,
        help="Parent directory for the run folder (suite cells use _raw_runs/).",
    )
    parser.add_argument(
        "--run-name",
        default=None,
        help="Exact run directory name under --output-root (no timestamp).",
    )
    parser.add_argument(
        "--hide-subagent-steps",
        action="store_true",
        help="Hide managed-agent (subagent) steps from console and agent.log.",
    )
    return parser


def main(argv: list[str] | None = None) -> None:
    load_dotenv(override=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )

    args = _build_parser().parse_args(argv)

    if args.list_profiles:
        for key in list_model_profiles():
            print(f"  {key}")
        return

    if not args.review:
        logger.error("--review is required (unless using --list-profiles).")
        sys.exit(2)

    if args.model_profile and any([args.model, args.backend, args.api_base]):
        logger.error(
            "--profile cannot be combined with --model, --backend, or --api-base."
        )
        sys.exit(2)

    selected_profile = get_selected_model_profile(args.model_profile)
    if selected_profile:
        logger.info("Model profile: %s", selected_profile)
    elif has_explicit_model_config(args.model, args.backend, args.api_base):
        logger.info(
            "Model: %s | Backend: %s | API base: %s",
            resolve_model_id(args.model),
            resolve_backend(args.backend),
            resolve_api_base(args.api_base) or "(default)",
        )

    try:
        run_review(
            review_json_path=args.review,
            model_id=args.model,
            backend=args.backend,
            api_base=args.api_base,
            model_profile=args.model_profile,
            include_subagent_steps=not args.hide_subagent_steps,
            batch_size=args.batch_size,
            output_root=Path(args.output_root) if args.output_root else None,
            run_name=args.run_name,
        )
    except ValueError as exc:
        logger.error("%s", exc)
        sys.exit(1)


if __name__ == "__main__":
    main()
