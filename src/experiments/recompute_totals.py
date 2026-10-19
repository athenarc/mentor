"""
CLI to rebuild cross-experiment screening totals from summary artifacts.

Reads canonical source registry or discovers experiment folders under
``output/screening_benchmarks`` depending on ``--source-mode``.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from experiments.harness.metrics import SCREENING_LABEL_POLICIES
from experiments.harness.totals import (
    DEFAULT_CANONICAL_POLICY,
    SOURCE_MODES,
    merge_canonical_sources,
    write_canonical_sources,
    write_screening_totals,
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Recompute aggregate totals from screening benchmark summaries."
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=None,
        help=(
            "Benchmark output root to scan. Defaults to "
            "data/output/screening_benchmarks."
        ),
    )
    parser.add_argument(
        "--totals-root",
        type=Path,
        default=None,
        help=(
            "Directory where regenerated totals are written. Defaults to "
            "<output-root>/totals."
        ),
    )
    parser.add_argument(
        "--source-mode",
        choices=SOURCE_MODES,
        default="canonical",
        help=(
            "Source selection for aggregate totals. 'canonical' reads "
            "totals/canonical_sources.json; 'discover' scans benchmark outputs "
            "with dedupe rules; 'all' scans benchmark outputs without suite-local "
            "dedupe. Default: canonical."
        ),
    )
    parser.add_argument(
        "--build-canonical-only",
        action="store_true",
        help=(
            "Build totals/canonical_sources.json from discovered completed/scored "
            "repeat=1 runs, then exit without regenerating aggregate totals."
        ),
    )
    parser.add_argument(
        "--merge-canonical-sources",
        nargs="+",
        type=Path,
        default=None,
        help=(
            "Merge one or more canonical_sources.json files into "
            "<totals-root>/canonical_sources.json before regenerating totals. "
            "The existing target manifest is included automatically."
        ),
    )
    parser.add_argument(
        "--merge-canonical-only",
        action="store_true",
        help=(
            "With --merge-canonical-sources, write the merged canonical manifest "
            "and exit without regenerating aggregate totals."
        ),
    )
    parser.add_argument(
        "--include-repeated-canonical-sources",
        action="store_true",
        help=(
            "When used with --build-canonical-only, allow repeated summaries in "
            "the seeded canonical manifest. By default only repeat=1 summaries "
            "are eligible."
        ),
    )
    parser.add_argument(
        "--include-repetition-folder-canonical-sources",
        action="store_true",
        help=(
            "When used with --build-canonical-only, allow sources from experiment "
            "folders whose names contain _repN. By default these folders are "
            "excluded from canonical seeding."
        ),
    )
    parser.add_argument(
        "--canonical-policy",
        choices=[*SCREENING_LABEL_POLICIES, "all"],
        default=DEFAULT_CANONICAL_POLICY,
        help=(
            "Canonical gold-label policy to use when building or reading "
            "canonical totals. Use 'all' to include every policy present in "
            "the canonical manifest. Default: exclude_label_0_5."
        ),
    )
    parser.add_argument(
        "--canonical-gold-label-policies",
        nargs="+",
        choices=list(SCREENING_LABEL_POLICIES),
        default=None,
        help=(
            "Gold-label policy summaries to include when building canonical "
            "sources. Overrides --canonical-policy. Kept for explicit "
            "multi-policy seeding."
        ),
    )
    parser.add_argument(
        "--write-incomplete-report",
        action="store_true",
        help=(
            "Write totals/incomplete_runs_report.json and .md with unscored "
            "runs and model groups excluded because one or more SRs were not scored."
        ),
    )
    args = parser.parse_args()
    if args.build_canonical_only and args.merge_canonical_sources:
        parser.error("--build-canonical-only cannot be combined with --merge-canonical-sources")
    if args.merge_canonical_only and not args.merge_canonical_sources:
        parser.error("--merge-canonical-only requires --merge-canonical-sources")
    if args.canonical_gold_label_policies is not None:
        canonical_gold_label_policies = args.canonical_gold_label_policies
    elif args.canonical_policy == "all":
        canonical_gold_label_policies = list(SCREENING_LABEL_POLICIES)
    else:
        canonical_gold_label_policies = [args.canonical_policy]

    if args.build_canonical_only:
        manifest = write_canonical_sources(
            output_root=args.output_root,
            totals_root=args.totals_root,
            include_repeated=args.include_repeated_canonical_sources,
            include_repetition_folders=args.include_repetition_folder_canonical_sources,
            gold_label_policies=canonical_gold_label_policies,
        )
        print("Canonical sources written under:")
        print(f"  {manifest['canonical_sources_path']}")
        print(f"Canonical sources: {manifest['n_sources']}")
        print(f"Eligible discovered runs: {manifest['n_eligible_runs']}")
        print(f"Excluded _repN folder runs: {manifest['n_excluded_repetition_folder_runs']}")
        print("Aggregate totals were not regenerated.")
        return

    if args.merge_canonical_sources:
        merged = merge_canonical_sources(
            source_manifest_paths=args.merge_canonical_sources,
            totals_root=args.totals_root,
        )
        print("Canonical sources merged under:")
        print(f"  {merged['canonical_sources_path']}")
        print(f"Input canonical sources: {merged['n_input_sources']}")
        print(f"Deduplicated sources: {merged['n_deduplicated_sources']}")
        print(f"Merged canonical sources: {merged['n_sources']}")
        if args.merge_canonical_only:
            print("Aggregate totals were not regenerated.")
            return

    result = write_screening_totals(
        output_root=args.output_root,
        totals_root=args.totals_root,
        source_mode=args.source_mode,
        canonical_gold_label_policies=canonical_gold_label_policies,
        write_incomplete_report=args.write_incomplete_report,
    )
    print(f"Totals refreshed under:\n  {result['totals_root']}")
    print(f"Source mode: {result['source_mode']}")
    if result["source_mode"] == "canonical":
        print(f"Canonical policy filter: {', '.join(canonical_gold_label_policies)}")
    print(f"Suite/policy/architecture groups: {len(result['groups'])}")
    print(
        "Horizontal comparison groups: "
        f"{len(result.get('horizontal_comparison_groups', []))}"
    )
    if result.get("incomplete_runs_report"):
        print(f"Incomplete runs report: {result['incomplete_runs_report']}")


if __name__ == "__main__":
    main()
