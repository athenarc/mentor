# Experiments

Root-level package (not under `src/`). Suite **execution** invokes Mentor
**externally** via `uv run mentor` / `python -m mentor.cli`. This package never
imports `mentor`.

```bash
uv run experiments suite --suite screening_ladder --profiles openai_gpt5 --batch-size 10
uv run experiments analyze data/experiments/output/screening_benchmarks/<suite_dir>
```

## Layout

- `config/suites.json` — suite registry
- `dataset/` — Cochrane CSV loaders (gold labels for scoring)
- `suites/` — grid expansion + subprocess runner
- `catalog.py` — reads `src/config/model_profiles.json` for labels / profile expansion
- `review_json.py` — writes Mentor-compatible `review.json`
- `harness/` — metrics, materialize, totals, reports

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
