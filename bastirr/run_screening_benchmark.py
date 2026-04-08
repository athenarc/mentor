"""
CLI entry point for the Gatekeeper screening benchmark harness.
"""

from __future__ import annotations

import argparse

from bastirr.benchmarking.model_presets import (
    CANONICAL_MODEL_PRESETS,
    list_model_presets,
)
from bastirr.benchmarking.review_suites import get_review_suite, list_review_suites
from bastirr.benchmarking.runner import run_screening_benchmark
from bastirr.benchmarking.metrics import SCREENING_LABEL_POLICIES


def _print_model_presets() -> None:
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


def _print_review_suite(suite_name: str) -> None:
    print(f"\nReviews in suite '{suite_name}':\n")
    for review in get_review_suite(suite_name):
        print(
            f"  {review.key} [{review.expected_n_studies} studies | "
            f"{review.expected_n_screen_pass} pass | {review.expected_n_screen_exclude} exclude]"
        )
        print(f"    split: {review.split}")
        print(f"    title: {review.title}")
        print(f"    url: {review.review_url}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run the Gatekeeper title/abstract screening benchmark."
    )
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
        "--gold-label-policy",
        choices=list(SCREENING_LABEL_POLICIES),
        default="include_label_0_5",
        help="How to interpret dataset label 0.5 when scoring saved screening decisions",
    )
    parser.add_argument(
        "--hide-subagent-steps",
        dest="include_subagent_steps",
        action="store_false",
        default=False,
        help="Hide sub-agent step details in activity.md",
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
    args = parser.parse_args()

    if args.list_suites:
        print("\nAvailable review suites:\n")
        for suite_name in list_review_suites():
            print(f"  {suite_name}")
        return

    if args.list_model_presets:
        _print_model_presets()
        return

    if args.list_reviews:
        _print_review_suite(args.suite)
        return

    experiment_dir, _summary = run_screening_benchmark(
        suite_name=args.suite,
        model_presets=args.model_presets,
        repeats=args.repeats,
        orchestrator_policy=args.orchestrator_policy,
        orchestrator_model_key=args.orchestrator_model,
        review_keys=args.reviews,
        gold_label_policy=args.gold_label_policy,
        include_subagent_steps=args.include_subagent_steps,
    )
    print(f"\nBenchmark complete. Results written to:\n  {experiment_dir}\n")


if __name__ == "__main__":
    main()
