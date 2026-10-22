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

Score a completed suite directory against Cochrane gold labels:

```bash
uv run experiments analyze data/experiments/output/screening_benchmarks/<suite_dir>
```

Analyze expects `_raw_runs/<cell>/run.json` + `evidence.json` (`screening_decisions`).
Derived from `run.json` → `screening_batch_size`:

- omitted / null → all studies in one Gatekeeper call (`batch`)
- `1` → single-study
- `N>1` → chunked

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
