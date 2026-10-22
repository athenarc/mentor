# Experiments

Run screening benchmark suites and score them against Cochrane gold labels.

From the repository root, after `uv sync` (and optionally
`uv sync --extra experiments` for dashboards/plots):

## Dataset

Suites and `analyze` need the Cochrane split CSVs under
`data/experiments/input/cochrane_sr_dataset/`.

Source: [Mendeley Data DOI 10.17632/7sgmg89zb6.1](https://doi.org/10.17632/7sgmg89zb6.1)
(Chan et al., 2025). Use `download.sh` to download only the split files needed for the experiments.

```bash
# From repo root
cd data/experiments/input/cochrane_sr_dataset && ./download.sh && cd ../../../..
```

## Running suites

```bash
uv run experiments suite --suite experiments_sep2026_biggest_reviews --profiles qwen3.5_27b-temp0 --batch-size 30 --repeats 3
```

Useful flags:

| Flag | Role |
|------|------|
| `--suite NAME` | Suite from `config/suites.json` (default: `screening_ladder`) |
| `--profiles KEY …` | Override suite `run.profiles` (keys from `src/config/model_profiles.json`) |
| `--reviews URL …` | Optional subset of suite review keys |
| `--repeats N` | Override suite repeats |
| `--batch-size N` | Override suite screening batch size |
| `--mode full\|screening-only` | Override suite mode (default: screening-only) |
| `--resume DIR` | Resume an existing experiment directory |
| `--hide-subagent-steps` | Quieter Mentor logs |
| `--list-suites` / `--list-profiles` / `--list-models` | Discovery helpers |

The command prints the experiment directory path when finished.

### Resume

If a suite stops mid-grid, continue in the **same** experiment directory with
`--resume` (reuse the same `--suite` / `--profiles` / `--batch-size` /
`--repeats` / `--reviews` as the original run):

```bash
uv run experiments suite --suite experiments_sep2026_biggest_reviews --profiles qwen3.5_27b-temp0 \
  --batch-size 30 --repeats 3 \
  --resume data/experiments/output/screening_benchmarks/experiments_sep2026_biggest_reviews_chunked_30_<stamp>
```

Resume skips any `_raw_runs/<run_name>/` whose `run.json` has
`"status": "completed"`, then runs the remaining review × profile × repeat
cells into that directory. Cell folder names end in `__r1`, `__r2`, … for the
repeat index (not “first review of the suite”).

### Outputs

Default layout:

```text
data/experiments/output/screening_benchmarks/
  <suite>_<architecture>_<YYYYMMDD_HHMMSS>/
    suite_manifest.json
    suite_results.json
    _raw_runs/<run_name>/
      review.json      # written by experiments
      evidence.json    # written by Mentor
      run.json         # Mentor + suite metadata patch
      …
```

Per cell, the runner passes Mentor `--output-root …/_raw_runs --run-name <run_name>`
so artifacts land in that cell folder (not under `data/mentor/output/`).

## Analyze

Score a completed suite directory against Cochrane gold labels. Suite execution
does **not** compute metrics; run analyze afterward:

```bash
uv run experiments analyze data/experiments/output/screening_benchmarks/<suite_dir>
```

Useful flags:

| Flag | Role |
|------|------|
| `--label-policies NAME …` | Subset of `include_label_0_5` / `exclude_label_0_5` (default: both) |
| `--execute-notebooks` | Also execute per-policy EDA notebooks |
| `--skip-totals` | Do not register this experiment in the totals registry |

### Inputs

Analyze expects each `_raw_runs/<cell>/` to have:

- `run.json` — suite metadata (`review_key`, `split`, `status`, …)
- `evidence.json` — Mentor `screening_decisions` (`study_index`, `decision`)

Architecture is inferred from `run.json` → `screening_batch_size`:

- omitted / null → all studies in one Gatekeeper call (`batch`)
- `1` → single-study
- `N>1` → chunked

### Metrics

For each cell, decisions are scored study-by-study against dataset gold labels.
**INCLUDE is the positive class.** Confusion counts:

| | Pred INCLUDE | Pred EXCLUDE |
|---|---|---|
| Gold INCLUDE | TP | FN |
| Gold EXCLUDE | FP | TN |

Then:

- **precision** = TP / (TP + FP)
- **recall** = TP / (TP + FN)
- **specificity** = TN / (TN + FP)
- **accuracy** = (TP + TN) / n_studies
- **F1** = 2 · P · R / (P + R)

Missing decisions count as EXCLUDE. Duplicate / invalid decisions are reported
separately and can mark a run incomplete for aggregate scoring.

### Gold-label policies

Policy names (defined in `experiments/harness/metrics.py` as
`SCREENING_LABEL_POLICIES`):

- `include_label_0_5`
- `exclude_label_0_5`

Cochrane labels are `1.0` (included), `0.5` (excluded after full text), and
`0.0` (excluded at title/abstract). Analyze materializes **both** policies by
default:

| Policy | Gold INCLUDE | Gold EXCLUDE |
|--------|--------------|--------------|
| `include_label_0_5` | `1.0`, `0.5` | `0.0` |
| `exclude_label_0_5` | `1.0` | `0.5`, `0.0` |

### What you get

Stdout prints a JSON summary (paths + raw-run count). On disk, under the same
experiment directory:

```text
<suite_dir>/
  include_label_0_5/          # (and exclude_label_0_5/)
    summary.json
    summary.csv               # per-run metrics (tp/fp/tn/fn, precision, recall, f1, …)
    leaderboard.md
    review_leaderboard.md
    screening_results_summary.html
    runs/<run_name>/          # policy view of that cell
  screening_policy_comparison.html   # side-by-side policies
  benchmark_checkpoint.json
```

More harness detail: [`harness/README.md`](harness/README.md).

## Layout

- `config/suites.json` — suite registry
- `dataset/` — Cochrane CSV loaders (gold labels for scoring)
- `suites/` — grid expansion + subprocess runner
- `catalog.py` — reads `src/config/model_profiles.json` for labels / profile expansion
- `review_json.py` — writes Mentor-compatible `review.json`
- `harness/` — metrics, materialize, totals, reports
- `streamlit_app/` / `benchmark_runs_ui.py` — screening dashboards
- `plot_screening_leaderboards.py` — leaderboard plots
- `sample_review_suites.py` — sample reviews into `suites.json`

Data (separate from Mentor):

- `data/experiments/input/cochrane_sr_dataset/` — CSVs via `download.sh`
- `data/experiments/output/screening_benchmarks/` — suite grids (gitignored)
- Mentor reviews/runs stay under `data/mentor/`

## Mentor boundary

Per cell the suite runner:

1. Loads a review from the dataset
2. Writes `_raw_runs/<cell>/review.json`
3. Runs `python -m mentor.cli --review … --profile … --output-root … --run-name …`
4. Patches suite metadata into `run.json`

Analyze scores `_raw_runs/*/evidence.json` against dataset gold labels.
