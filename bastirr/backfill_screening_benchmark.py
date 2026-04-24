"""
CLI entry point for backfilling legacy flat screening benchmark directories.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from bastirr.benchmarking.backfill import backfill_policy_views
from bastirr.benchmarking.metrics import SCREENING_LABEL_POLICIES


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Backfill a legacy flat screening benchmark directory into per-policy subfolders."
    )
    parser.add_argument(
        "experiment_dir",
        type=Path,
        help="Path to the legacy benchmark directory",
    )
    parser.add_argument(
        "--gold-label-policies",
        nargs="+",
        choices=list(SCREENING_LABEL_POLICIES),
        default=None,
        help="Optional subset of policies to materialize",
    )
    parser.add_argument(
        "--skip-policy-notebook-execution",
        action="store_true",
        help="Generate policy results-analysis notebooks without executing them",
    )
    args = parser.parse_args()

    result = backfill_policy_views(
        args.experiment_dir,
        label_policies=args.gold_label_policies,
        execute_policy_notebooks=not args.skip_policy_notebook_execution,
    )
    print(f"\nBackfill complete. Results written to:\n  {result['experiment_dir']}\n")


if __name__ == "__main__":
    main()
