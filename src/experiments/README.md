# Experiments

Research and evaluation entrypoints for screening benchmarks.

These modules depend on `mentor` (runtime, agents, tools). Core never imports
`experiments`.

## Run

```bash
uv sync --extra experiments --extra dev
uv run python -m experiments.screening --list-suites
uv run python -m experiments.screening --suite screening_ladder --model-presets openai_gpt5
uv run python -m experiments.screening_loop --suite screening_ladder --loop-mode chunked --chunk-size 10
```

## Layout

- `screening.py` / `screening_loop.py` — thin CLIs
- `config/` — suite and model-preset registries (`suites.json`, `models.json`)
- `harness/` — benchmark runners, metrics, checkpoints
- `prompts/` — experiment-only agent instructions (passed into `mentor` factories via `instructions=`)
- `sample_review_suites.py` — dataset sampling CLI (distinct from the experiment suite registry in `config/suites.json`)
- `benchmark_runs_ui.py` + `streamlit_app/` — Streamlit dashboard for screening benchmark results
- `plot_screening_leaderboards.py` — charts from totals / review leaderboard markdown

## Streamlit dashboard

```bash
uv run streamlit run src/experiments/benchmark_runs_ui.py -- path/to/benchmark_results_dir
```

## Leaderboard plots

```bash
uv run python -m experiments.plot_screening_leaderboards
```

See also `harness/README.md` and `harness/CHUNKED_LOOP_RUNS.md` for harness details.
