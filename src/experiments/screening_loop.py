"""
CLI for looped Gatekeeper screening benchmarks (``experiments.harness.loop_runner``).

``--loop-mode single-study`` screens one study per orchestrator step;
``chunked`` uses bounded mini-batches via ``--chunk-count`` / ``--chunk-size``.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from experiments.cli_common import (
    add_shared_screening_args,
    finalize_benchmark_run,
    handle_list_flags,
)
from experiments.harness.loop_runner import (
    rerun_screening_loop_reviews_in_experiment,
    run_screening_loop_benchmark,
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run the looped Gatekeeper title/abstract screening benchmark."
    )
    add_shared_screening_args(
        parser,
        rerun_help=(
            "Existing loop benchmark experiment directory to update by rerunning "
            "the review keys passed with --reviews"
        ),
    )
    parser.add_argument(
        "--loop-mode",
        choices=["single-study", "chunked"],
        default="single-study",
        help=(
            "Loop benchmark mode. 'single-study' runs one Gatekeeper call per "
            "study; 'chunked' runs bounded mini-batches through the Orchestrator."
        ),
    )
    parser.add_argument(
        "--chunk-count",
        type=int,
        default=None,
        help="Optional number of chunks per review when --loop-mode=chunked",
    )
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=None,
        help="Optional maximum studies per chunk when --loop-mode=chunked",
    )
    parser.add_argument(
        "--orchestrator-max-steps",
        type=int,
        default=None,
        help=(
            "Maximum smolagents CodeAgent steps for each loop Orchestrator call. "
            "Defaults to 20 for both single-study and chunked loop modes."
        ),
    )
    args = parser.parse_args()

    if handle_list_flags(args):
        return

    if args.rerun_in_experiment:
        if not args.reviews:
            parser.error("--rerun-in-experiment requires --reviews")
        experiment_dir, _summary = rerun_screening_loop_reviews_in_experiment(
            experiment_dir=Path(args.rerun_in_experiment),
            review_keys=args.reviews,
            include_subagent_steps=args.include_subagent_steps,
            execute_policy_notebooks=not args.skip_policy_notebook_execution,
            orchestrator_max_steps=args.orchestrator_max_steps,
        )
    else:
        experiment_dir, _summary = run_screening_loop_benchmark(
            suite_name=args.suite,
            model_presets=args.model_presets,
            repeats=args.repeats,
            orchestrator_policy=args.orchestrator_policy,
            orchestrator_model_key=args.orchestrator_model,
            review_keys=args.reviews,
            include_subagent_steps=args.include_subagent_steps,
            execute_policy_notebooks=not args.skip_policy_notebook_execution,
            loop_mode=args.loop_mode,
            chunk_count=args.chunk_count,
            chunk_size=args.chunk_size,
            orchestrator_max_steps=args.orchestrator_max_steps,
            canonical_mode=args.canonical,
        )
    finalize_benchmark_run(
        experiment_dir,
        canonical_mode=args.canonical,
        skip_totals_aggregation=args.skip_totals_aggregation,
        completion_label="Loop benchmark complete.",
    )


if __name__ == "__main__":
    main()
