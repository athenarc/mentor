# Screening Benchmark Totals

This folder contains aggregate views of screening benchmark runs. The current
default aggregation source is `canonical_sources.json`, not a blind scan of
every benchmark output folder.

## Main Files

- `canonical_sources.json`: explicit list of run rows that count toward totals.
- `totals_index.json`: index of generated totals folders. Paths are relative to
  the project root.

## Suite Totals

Each suite has policy and architecture subfolders:

```text
<suite>/exclude_policy/<architecture>/
```

Important files inside each architecture folder:

- `totals_leaderboard.md`: model-level leaderboard for that suite.
- `totals_leaderboard.json`: same data, plus metadata and excluded incomplete
  model groups.
- `totals_review_leaderboard.md`: per-review model results.
- `totals_review_leaderboard.json`: machine-readable per-review results.
- `per_sr/`: one leaderboard per individual review key.

Totals currently use the `exclude_label_0_5` policy as canonical by default.
Use `--canonical-policy include_label_0_5` or `--canonical-policy all` when
regenerating totals if the canonical manifest contains additional policy views.

## Completeness Rule

Model-level leaderboard entries are included only when the model has scored all
reviews expected by the source summary for that suite/run shape. Incomplete
model groups are not ranked, because partial averages can be misleading.

Excluded groups are still recorded in `totals_leaderboard.json` under:

```json
"excluded_incomplete_model_groups"
```

For example, an interrupted or incomplete `2/5` run will not compete against
models with complete `5/5` runs.

For a consolidated diagnostic view of incomplete runs, regenerate totals with:

```bash
venv/bin/python -m bastirr.recompute_screening_totals \
  --source-mode canonical \
  --write-incomplete-report
```

This writes:

- `incomplete_runs_report.json`
- `incomplete_runs_report.md`

The report lists unscored source rows and model groups excluded because one or
more SRs were not scored. For canonical totals, the diagnostic scans current
summary files with the canonical policy filter, because `canonical_sources.json`
contains only completed/scored rows.

## Horizontal Comparison

`horizontal_comparison/` aggregates across suites by size band and architecture.
Use this for cross-suite size-band comparisons, especially once future benchmark
sets are organized primarily by review size rather than by screening ladder.

Size bands:

- `small_10`: up to 15 studies
- `lower_mid_25`: 16-35 studies
- `mid_50`: 36-65 studies
- `upper_mid_100`: 66-100 studies
- `large_100_plus`: 100+ studies

## Regenerating Totals

After adding completed benchmark runs, regenerate totals with:

```bash
venv/bin/python -m bastirr.recompute_screening_totals --source-mode canonical
```

To regenerate canonical totals for a different policy:

```bash
venv/bin/python -m bastirr.recompute_screening_totals --source-mode canonical --canonical-policy include_label_0_5
```

To rebuild only the canonical source manifest from discovered completed/scored
repeat-1 runs:

```bash
venv/bin/python -m bastirr.recompute_screening_totals --build-canonical-only
```

To build a manifest containing both policies:

```bash
venv/bin/python -m bastirr.recompute_screening_totals --build-canonical-only --canonical-policy all
```

## Merging Totals From Another Machine

When benchmark outputs are copied from another machine, keep one totals folder
as the target `totals/` folder and place the other machine's previous totals
folder elsewhere, for example `totals_loc/`.

Merge canonical manifests and regenerate all aggregate totals with:

```bash
venv/bin/python -m bastirr.recompute_screening_totals \
  --merge-canonical-sources bastirr/output/screening_benchmarks/totals_loc/canonical_sources.json \
  --source-mode canonical
```

The command includes the existing `totals/canonical_sources.json`
automatically, unions it with the supplied manifest, deduplicates matching
canonical entries by newest source timestamp, writes the merged
`totals/canonical_sources.json`, and regenerates `totals_index.json` plus all
leaderboards.

Use manifest rebuilding carefully: `canonical_sources.json` is the source of
truth for which runs are considered canonical.
