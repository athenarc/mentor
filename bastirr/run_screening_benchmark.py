"""
CLI entry point for the Gatekeeper screening benchmark harness.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from bastirr.benchmarking.model_presets import (
    CANONICAL_MODEL_PRESETS,
    list_model_presets,
)
from bastirr.benchmarking.review_suites import get_review_suite, list_review_suites

from bastirr.benchmarking.runner import (
    rerun_screening_reviews_in_experiment,
    run_screening_benchmark,
)
from bastirr.benchmarking.totals import (
    register_canonical_sources_from_experiment,
    write_screening_totals,
)


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
        "--orchestrator-max-steps",
        type=int,
        default=20,
        help="Maximum smolagents CodeAgent steps for the batch Orchestrator.",
    )
    parser.add_argument(
        "--rerun-in-experiment",
        default=None,
        help=(
            "Existing batch benchmark experiment directory to update by rerunning "
            "the review keys passed with --reviews"
        ),
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

    if args.rerun_in_experiment:
        if not args.reviews:
            parser.error("--rerun-in-experiment requires --reviews")
        experiment_dir, _summary = rerun_screening_reviews_in_experiment(
            experiment_dir=Path(args.rerun_in_experiment),
            review_keys=args.reviews,
            include_subagent_steps=args.include_subagent_steps,
            execute_policy_notebooks=not args.skip_policy_notebook_execution,
            orchestrator_max_steps=args.orchestrator_max_steps,
        )
    else:
        experiment_dir, _summary = run_screening_benchmark(
            suite_name=args.suite,
            model_presets=args.model_presets,
            repeats=args.repeats,
            orchestrator_policy=args.orchestrator_policy,
            orchestrator_model_key=args.orchestrator_model,
            review_keys=args.reviews,
            include_subagent_steps=args.include_subagent_steps,
            execute_policy_notebooks=not args.skip_policy_notebook_execution,
            canonical_mode=args.canonical,
            orchestrator_max_steps=args.orchestrator_max_steps,
        )
    canonical_info = register_canonical_sources_from_experiment(
        experiment_dir,
        mode=args.canonical,
    )
    totals_info = None
    if not args.skip_totals_aggregation:
        totals_info = write_screening_totals(source_mode="canonical")
    print(f"\nBenchmark complete. Results written to:\n  {experiment_dir}\n")
    if canonical_info.get("canonical_sources_path"):
        print(
            "Canonical sources updated:\n"
            f"  {canonical_info['canonical_sources_path']}\n"
            f"  registered entries: {canonical_info['registered_sources']}\n"
        )
    if totals_info:
        print(f"Totals refreshed under:\n  {totals_info['totals_root']}\n")


if __name__ == "__main__":
    main()
