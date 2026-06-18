"""
CLI entry point for backfilling legacy flat screening benchmark directories.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from bastirr.benchmarking.backfill import (
    backfill_missing_policy_views,
    backfill_policy_views,
)
from bastirr.benchmarking.metrics import SCREENING_LABEL_POLICIES


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Backfill screening benchmark policy views for legacy flat or "
            "checkpointed experiment directories."
        )
    )
    parser.add_argument(
        "experiment_dir",
        type=Path,
        nargs="?",
        help="Path to one benchmark experiment directory",
    )
    parser.add_argument(
        "--all-missing",
        action="store_true",
        help="Scan the screening benchmark output root and backfill experiments missing policy outputs",
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=None,
        help="Benchmark output root used with --all-missing. Defaults to bastirr/output/screening_benchmarks.",
    )
    parser.add_argument(
        "--gold-label-policies",
        nargs="+",
        choices=list(SCREENING_LABEL_POLICIES),
        default=None,
        help="Optional subset of policies to materialize. Defaults to both built-in policies.",
    )
    parser.add_argument(
        "--overwrite-existing-policies",
        action="store_true",
        help="Regenerate existing policy folders as well as missing ones",
    )
    parser.add_argument(
        "--skip-policy-notebook-execution",
        action="store_true",
        help="Generate policy results-analysis notebooks without executing them",
    )
    args = parser.parse_args()

    if args.all_missing:
        result = backfill_missing_policy_views(
            output_root=args.output_root,
            label_policies=args.gold_label_policies,
            execute_policy_notebooks=not args.skip_policy_notebook_execution,
            overwrite_existing_policies=args.overwrite_existing_policies,
        )
        print(f"\nBackfill scan complete under:\n  {result['output_root']}")
        print(f"Checkpointed experiments scanned: {result['scanned_experiments']}")
        print(f"Experiments backfilled: {result['backfilled_experiments']}")
        if result["errors"]:
            print("Errors:")
            for error in result["errors"]:
                print(f"  {error['experiment_dir']}: {error['error']}")
        return

    if args.experiment_dir is None:
        parser.error("experiment_dir is required unless --all-missing is used")

    result = backfill_policy_views(
        args.experiment_dir,
        label_policies=args.gold_label_policies,
        execute_policy_notebooks=not args.skip_policy_notebook_execution,
        overwrite_existing_policies=args.overwrite_existing_policies,
    )
    print(f"\nBackfill complete. Results written to:\n  {result['experiment_dir']}")
    print(f"Materialized policies: {', '.join(result.get('materialized_policies', [])) or 'none'}")
    print(f"Existing policies kept: {', '.join(result.get('skipped_existing_policies', [])) or 'none'}")
    print("")


if __name__ == "__main__":
    main()
