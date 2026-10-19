"""
CLI for the batch Gatekeeper screening benchmark (``experiments.harness.runner``).

Default architecture: thin orchestrator delegates one batch gatekeeper call per
review; results land under ``output/screening_benchmarks/<timestamp>_…``.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from experiments.cli_common import (
    add_shared_screening_args,
    finalize_benchmark_run,
    handle_list_flags,
)
from experiments.harness.runner import (
    rerun_screening_reviews_in_experiment,
    run_screening_benchmark,
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run the Gatekeeper title/abstract screening benchmark."
    )
    add_shared_screening_args(
        parser,
        rerun_help=(
            "Existing batch benchmark experiment directory to update by rerunning "
            "the review keys passed with --reviews"
        ),
    )
    parser.add_argument(
        "--orchestrator-max-steps",
        type=int,
        default=20,
        help="Maximum smolagents CodeAgent steps for the batch Orchestrator.",
    )
    args = parser.parse_args()

    if handle_list_flags(args):
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
    finalize_benchmark_run(
        experiment_dir,
        canonical_mode=args.canonical,
        skip_totals_aggregation=args.skip_totals_aggregation,
        completion_label="Benchmark complete.",
    )


if __name__ == "__main__":
    main()
