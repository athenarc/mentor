"""CLI: score Mentor suite experiment directories (analysis only)."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from experiments.harness.analysis import analyze_experiment


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Analyze a Mentor suite experiment directory: score evidence.json "
            "against gold labels and write summary/leaderboard artifacts."
        )
    )
    parser.add_argument(
        "experiment_dir",
        type=Path,
        help="Path to the suite experiment directory (contains _raw_runs/)",
    )
    parser.add_argument(
        "--label-policies",
        nargs="+",
        default=None,
        help="Optional subset of gold label policies to materialize",
    )
    parser.add_argument(
        "--execute-notebooks",
        action="store_true",
        help="Execute per-policy EDA notebooks after materializing summaries",
    )
    parser.add_argument(
        "--skip-totals",
        action="store_true",
        help="Do not register this experiment in the totals registry",
    )
    args = parser.parse_args()

    summary = analyze_experiment(
        args.experiment_dir,
        label_policies=args.label_policies,
        execute_policy_notebooks=args.execute_notebooks,
        register_totals=not args.skip_totals,
    )
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
