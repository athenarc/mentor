# Experiments

Screening benchmarks that evaluate Gatekeeper title/abstract screening without
running Miner/Critic. These modules depend on `mentor` (runtime, agents, tools);
`mentor` never imports `experiments`.

Experiment-only prompts under `prompts/` are passed into Mentor agent factories
at runtime via `instructions=`.

## Setup

```bash
uv sync --extra experiments --extra dev
```

Suite and model-preset registries (edit without touching Python):

- `config/suites.json`
- `config/models.json`

Most presets use OpenRouter. Set in `.env`:

```bash
OPENROUTER_API_KEY=sk-or-v1-...
OPENROUTER_API_BASE=https://openrouter.ai/api/v1
```

The Cochrane dataset under `data/input/systematic_review_dataset/` is required
(same as the production workflow). See the root README setup section.

## Layout

- `cli.py` — console entrypoint (`uv run experiments <command>`)
- `screening.py` / `screening_loop.py` — batch / loop benchmark CLIs
- `config/` — suite and model-preset registries (`suites.json`, `models.json`)
- `harness/` — benchmark runners, metrics, checkpoints
- `prompts/` — experiment-only agent instructions
- `sample_review_suites.py` — dataset sampling CLI (distinct from the suite registry in `config/suites.json`)
- `benchmark_runs_ui.py` + `streamlit_app/` — Streamlit dashboard for screening benchmark results
- `plot_screening_leaderboards.py` — charts from totals / review leaderboard markdown

Harness internals: [`harness/README.md`](harness/README.md) and
[`harness/CHUNKED_LOOP_RUNS.md`](harness/CHUNKED_LOOP_RUNS.md).

Commands: `screening`, `screening-loop`, `recompute-totals`, `backfill`,
`html-report`, `sample-review-suites`, `plot-leaderboards`.

## Discover suites, presets, and reviews

```bash
uv run experiments screening --list-suites
uv run experiments screening --list-model-presets
uv run experiments screening --suite screening_ladder --list-reviews
```

Current suites include `screening_ladder`, `screening_ladder_dev_*`,
`experiments_aug2026`, and `experiments_sep2026_biggest_reviews`. Presets
include e.g. `openai_gpt5`, `deepseek_v4_pro`, `kimi_k2.6`, …

## Batch screening benchmark

One Orchestrator call screens the **full candidate list** for each review
(thin orchestrator + real Gatekeeper). There is no batch/chunk size flag and
the suite does not define one — `suites.json` only lists which reviews to run
(`expected_n_studies` is metadata).

```bash
# Full default suite, all model presets (expensive)
uv run experiments screening --suite screening_ladder

# Recommended smoke / iterative shape: one suite × one model × one review
uv run experiments screening \
  --suite screening_ladder \
  --reviews stroke_theophylline_10 \
  --model-presets openai_gpt5 \
  --orchestrator-policy fixed \
  --orchestrator-model openai_gpt5 \
  --repeats 1

# Several models
uv run experiments screening \
  --suite screening_ladder \
  --model-presets openai_gpt5 deepseek_v4_pro \
  --repeats 1
```

Useful flags:

| Flag | Meaning |
|------|---------|
| `--suite` | Review suite key (default `screening_ladder`) |
| `--reviews …` | Subset of review keys inside the suite |
| `--model-presets …` | Gatekeeper presets (`all` by default) |
| `--repeats N` | Repeated runs per model/review pair |
| `--orchestrator-policy fixed\|match-gatekeeper` | Thin orchestrator model selection |
| `--orchestrator-model` | Preset when policy is `fixed` (default `openai_gpt5`) |
| `--orchestrator-max-steps` | Max CodeAgent steps for the batch orchestrator |
| `--canonical auto\|none\|force` | Register completed repeat=1 runs into totals |
| `--skip-totals-aggregation` | Skip refreshing aggregate totals |
| `--skip-policy-notebook-execution` | Write notebooks without executing them |
| `--rerun-in-experiment DIR` | Re-run selected `--reviews` inside an existing experiment |

Rerun a failed review in place:

```bash
uv run experiments screening \
  --rerun-in-experiment data/output/screening_benchmarks/<timestamp>_screening_ladder \
  --reviews heart_failure_mhealth_200 \
  --skip-policy-notebook-execution \
  --canonical auto
```

## Looped screening benchmark

Same suites/presets/scoring, but different topology:

- `single-study` — one Gatekeeper call per study
- `chunked` — bounded mini-batches through the Orchestrator

Chunk size is a **CLI flag** (`--chunk-size` or `--chunk-count`), not a suite
field. Use only one of those two flags with `--loop-mode chunked`.

```bash
# Single-study loop
uv run experiments screening-loop \
  --suite screening_ladder \
  --reviews stroke_theophylline_10 \
  --model-presets openai_gpt5 \
  --loop-mode single-study \
  --orchestrator-policy fixed \
  --orchestrator-model openai_gpt5

# Chunked loop: screen in mini-batches of 10 studies
uv run experiments screening-loop \
  --suite screening_ladder \
  --reviews stroke_theophylline_10 \
  --model-presets deepseek_v4_pro \
  --loop-mode chunked \
  --chunk-size 10 \
  --orchestrator-policy fixed \
  --orchestrator-model deepseek_v4_pro \
  --repeats 1 \
  --canonical auto

# Same idea, but fix the number of chunks instead of their size
uv run experiments screening-loop \
  --suite screening_ladder \
  --reviews stroke_theophylline_10 \
  --model-presets deepseek_v4_pro \
  --loop-mode chunked \
  --chunk-count 4 \
  --orchestrator-policy fixed \
  --orchestrator-model deepseek_v4_pro \
  --repeats 1
```

Chunked runbook details: [`harness/CHUNKED_LOOP_RUNS.md`](harness/CHUNKED_LOOP_RUNS.md).

## Experiment outputs

```text
data/output/screening_benchmarks/<timestamp>_<suite>/                 # batch
data/output/screening_benchmarks/<timestamp>_<suite>_loop_<model>/    # loop (shape varies)
  include_policy/ / exclude_policy/   # gold-label policy views
    runs/<review>_<preset>_…/         # evidence.json, metrics.json, workflow.log, …
    summary.json / summary.csv
    leaderboard.md / review_leaderboard.md
    screening_results_summary.html
  … checkpoints, comparison HTML when both policies exist …

data/output/screening_benchmarks/totals/   # aggregate leaderboards across experiments
```

Two gold-label policies are always materialised: treat Cochrane label `0.5` as
include vs exclude (`include_policy` / `exclude_policy`).

## Helper CLIs

```bash
# Regenerate aggregate totals
uv run experiments recompute-totals

# Backfill policy views for an older experiment directory
uv run experiments backfill data/output/screening_benchmarks/<experiment_dir>

# HTML summary for one experiment or policy folder
uv run experiments html-report data/output/screening_benchmarks/<experiment_dir>

# Sample new review suites from the dataset (writes suite JSON; separate from the harness registry)
uv run experiments sample-review-suites sample --help
```

## Streamlit dashboard

```bash
uv run streamlit run src/experiments/benchmark_runs_ui.py -- path/to/benchmark_results_dir
```

## Leaderboard plots

```bash
uv run experiments plot-leaderboards
```

## Tests

```bash
uv run pytest
```
