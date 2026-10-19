"""
Shared CLI flags and post-run hooks for screening benchmark commands.

``add_shared_screening_args`` registers suite/model/repeat/canonical options;
``finalize_benchmark_run`` updates canonical source registry and aggregate totals.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from experiments.harness.model_presets import (
    CANONICAL_MODEL_PRESETS,
    list_model_presets,
)
from experiments.harness.review_suites import get_review_suite, list_review_suites
from experiments.harness.totals import (
    register_canonical_sources_from_experiment,
    write_screening_totals,
)


def print_model_presets() -> None:
    print("\nAvailable model presets:\n")
    for key in list_model_presets():
        resolved = CANONICAL_MODEL_PRESETS[key].resolve(strict=False)
        api_base = resolved.api_base or "(default provider endpoint)"
        print(f"  {resolved.key}")
        print(f"    label: {resolved.model_label}")
        print(f"    backend: {resolved.backend}")
        print(f"    model_id: {resolved.model_id}")
        print(f"    api_base: {api_base}")
        print(f"    api_key_source: {resolved.api_key_source}")


def print_review_suite(suite_name: str) -> None:
    print(f"\nReviews in suite '{suite_name}':\n")
    for review in get_review_suite(suite_name):
        print(
            f"  {review.key} [{review.expected_n_studies} studies | "
            f"{review.expected_n_screen_pass} pass | {review.expected_n_screen_exclude} exclude]"
        )
        print(f"    split: {review.split}")
        print(f"    title: {review.title}")
        print(f"    url: {review.review_url}")


def print_suite_names() -> None:
    print("\nAvailable review suites:\n")
    for name in list_review_suites():
        print(f"  {name}")


def add_shared_screening_args(
    parser: argparse.ArgumentParser,
    *,
    rerun_help: str,
) -> None:
    """Register flags shared by batch and loop screening CLIs."""
    parser.add_argument(
        "--suite",
        default="screening_ladder",
        help="Review suite to benchmark",
    )
    parser.add_argument(
        "--reviews",
        nargs="+",
        default=None,
        help="Optional subset of review keys within the selected suite",
    )
    parser.add_argument(
        "--model-presets",
        nargs="+",
        default=["all"],
        help="Gatekeeper model presets to run (default: all)",
    )
    parser.add_argument(
        "--repeats",
        type=int,
        default=1,
        help="Number of repeated runs per model/review pair",
    )
    parser.add_argument(
        "--orchestrator-policy",
        choices=["fixed", "match-gatekeeper"],
        default="fixed",
        help="How to choose the thin orchestrator model",
    )
    parser.add_argument(
        "--orchestrator-model",
        default="openai_gpt5",
        help="Preset key used when --orchestrator-policy=fixed",
    )
    parser.add_argument(
        "--hide-subagent-steps",
        dest="include_subagent_steps",
        action="store_false",
        default=False,
        help="Hide sub-agent step details in activity.md",
    )
    parser.add_argument(
        "--skip-policy-notebook-execution",
        action="store_true",
        help="Generate policy results-analysis notebooks without executing them",
    )
    parser.add_argument(
        "--skip-totals-aggregation",
        action="store_true",
        help="Do not refresh aggregate totals after the benchmark completes",
    )
    parser.add_argument(
        "--canonical",
        choices=["auto", "none", "force"],
        default="auto",
        help=(
            "Canonical registry behavior after the benchmark completes. "
            "'auto' registers completed/scored repeat=1 runs, 'none' leaves "
            "canonical_sources.json unchanged, and 'force' can register repeated runs."
        ),
    )
    parser.add_argument(
        "--rerun-in-experiment",
        default=None,
        help=rerun_help,
    )
    parser.add_argument(
        "--list-suites",
        action="store_true",
        help="List the available review suites and exit",
    )
    parser.add_argument(
        "--list-model-presets",
        action="store_true",
        help="List the available model presets and exit",
    )
    parser.add_argument(
        "--list-reviews",
        action="store_true",
        help="List the reviews in the selected suite and exit",
    )


def handle_list_flags(args: argparse.Namespace) -> bool:
    """Handle --list-* flags. Returns True if the process should exit."""
    if args.list_suites:
        print_suite_names()
        return True
    if args.list_model_presets:
        print_model_presets()
        return True
    if args.list_reviews:
        print_review_suite(args.suite)
        return True
    return False


def finalize_benchmark_run(
    experiment_dir: Path,
    *,
    canonical_mode: str,
    skip_totals_aggregation: bool,
    completion_label: str,
) -> dict[str, Any]:
    """Register canonical sources, refresh totals, and print the footer."""
    canonical_info = register_canonical_sources_from_experiment(
        experiment_dir,
        mode=canonical_mode,
    )
    totals_info = None
    if not skip_totals_aggregation:
        totals_info = write_screening_totals(source_mode="canonical")

    print(f"\n{completion_label} Results written to:\n  {experiment_dir}\n")
    if canonical_info.get("canonical_sources_path"):
        print(
            "Canonical sources updated:\n"
            f"  {canonical_info['canonical_sources_path']}\n"
            f"  registered entries: {canonical_info['registered_sources']}\n"
        )
    if totals_info:
        print(f"Totals refreshed under:\n  {totals_info['totals_root']}\n")
    return {"canonical": canonical_info, "totals": totals_info}
