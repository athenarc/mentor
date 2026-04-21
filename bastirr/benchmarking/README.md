# Screening Benchmark Workflow

This document describes the experimental screening benchmark harness on this
branch. It is intentionally separate from the main Bastirr README because the
benchmark is a branch-specific evaluation workflow rather than the primary
runtime path.

## Purpose

The benchmark isolates the title/abstract screening phase so we can evaluate
the Gatekeeper agent without paying for the full 5-agent Bastirr pipeline.

The harness keeps the important architectural boundary from the main system:

- the Orchestrator sees only protocol text
- the review with full candidate studies is loaded into the existing in-memory
  store first
- the thin screening Orchestrator retrieves candidates through
  `get_candidates_json()`
- the real Gatekeeper performs screening
- the run artifacts are written deterministically after screening

This gives us a fairer screening benchmark while reusing the real Gatekeeper
implementation and the same review data loader.

Both the review suites and the model presets are now file-backed so they can
be edited without touching Python code:

- `bastirr/benchmarking/config/review_suites.json`
- `bastirr/benchmarking/config/model_presets.json`

## Workflow Overview

The benchmark execution path is:

1. `bastirr/run_screening_benchmark.py` resolves the review suite, model
   presets, orchestrator policy, and repeat count.
2. `bastirr/benchmarking/runner.py` loads one Cochrane review from the dataset.
3. `review_to_json()` converts the full review, including studies.
4. `load_review_data()` stores that payload in the shared search store.
5. The thin screening Orchestrator receives only protocol text:
   - review title
   - background
   - objective
   - selection criteria
   - output directory
6. The thin screening Orchestrator calls `get_candidates_json()`.
7. The thin screening Orchestrator delegates screening to the real Gatekeeper.
8. The screening saver writes a screening-only `evidence.json`.
9. Deterministic benchmark code computes metrics and inspection artifacts from:
   - the saved screening decisions
   - the dataset gold labels
   - the original review object
10. If the saved screening output is incomplete, the harness automatically
    retries the screening run once with stricter completion instructions.
11. The screening saver fails closed when the parsed decision count does not
    match the expected number of studies, so partial outputs are not silently
    persisted as valid benchmark artifacts.
12. The harness writes per-run and experiment-level summaries.

## Components

Key files:

- `bastirr/run_screening_benchmark.py`
- `bastirr/agents/screening_orchestrator.py`
- `bastirr/tools/screening_benchmark_tools.py`
- `bastirr/benchmarking/review_suites.py`
- `bastirr/benchmarking/model_presets.py`
- `bastirr/benchmarking/metrics.py`
- `bastirr/benchmarking/inspection.py`
- `bastirr/benchmarking/runner.py`

Responsibilities:

- `screening_orchestrator.py`: thin manager that does retrieval plus
  Gatekeeper delegation only, and is explicitly forbidden from reconstructing
  screening decisions itself
- `screening_benchmark_tools.py`: screening-only persistence and short summary
- `review_suites.py`: locked benchmark review registries
- `model_presets.py`: named Gatekeeper and orchestrator model presets
- `metrics.py`: gold-label mapping and study-level metrics
- `inspection.py`: study-by-study gold-vs-prediction comparison artifacts
- `runner.py`: experiment loop, logging, metrics, summaries, and output layout

## Gold Label Policy

The benchmark evaluates title/abstract screening rather than final-review
inclusion. Gold labels are mapped like this:

- `1.0` -> `INCLUDE`
- `0.5` -> `INCLUDE`
- `0.0` -> `EXCLUDE`

Why:

- `1.0` means the study was included in the final review
- `0.5` means it survived title/abstract screening but was excluded later,
  usually after fuller assessment
- `0.0` means it should have been excluded at screening

The inspection artifacts also preserve the final-review meaning:

- `included_in_review`
- `excluded_after_full_text`
- `excluded_at_screening`

This mapping is now configurable per benchmark run with `--gold-label-policy`:

- `include_label_0_5`: `1.0` and `0.5` count as `INCLUDE`
- `exclude_label_0_5`: only `1.0` counts as `INCLUDE`

## Locked Review Suite

The default suite is `screening_ladder`. It is a fixed ladder of escalating review
sizes:

| Key | Split | Studies | Gold Pass | Gold Exclude |
|-----|-------|---------|-----------|--------------|
| `stroke_theophylline_10` | `val` | 10 | 6 | 4 |
| `alopecia_areata_25` | `random_test` | 25 | 17 | 8 |
| `iud_insertion_pain_50` | `random_test` | 50 | 30 | 20 |
| `pelvic_floor_training_100` | `random_test` | 100 | 48 | 52 |
| `heart_failure_mhealth_200` | `heart_test` | 200 | 137 | 63 |

The suite definitions live in `bastirr/benchmarking/config/review_suites.json`.

Useful discovery commands:

```bash
PYTHONPATH=. python3 -m bastirr.run_screening_benchmark --list-suites
PYTHONPATH=. python3 -m bastirr.run_screening_benchmark --list-reviews
```

## Model Presets

The benchmark uses named presets so a single run can evaluate a matrix of
models without mutating the generic one-model Bastirr config for every run.
The preset definitions live in `bastirr/benchmarking/config/model_presets.json`.

Built-in presets:

- `openai_gpt5`
- `deepseek_v3_2_thinking`
- `ollama_qwen3_5_27b_bf16`

Current meanings:

- `openai_gpt5`: `gpt-5` via the OpenAI API
- `deepseek_v3_2_thinking`: `deepseek-reasoner`, which corresponds to DeepSeek V3.2
  with Thinking enabled
- `ollama_qwen3_5_27b_bf16`: `qwen3.5:27b-bf16` via Ollama's OpenAI-compatible API at
  `http://localhost:11434/v1`

The persisted benchmark artifacts store both:

- the preset key for reproducibility
- the resolved model label for human inspection and long-lived leaderboards

Useful command:

```bash
PYTHONPATH=. python3 -m bastirr.run_screening_benchmark --list-model-presets
```

## Environment Variables

The generic Bastirr model configuration still exists and is still useful for
single-model runs:

- `BASTIRR_MODEL_BACKEND`
- `BASTIRR_MODEL`
- `BASTIRR_API_BASE`
- `BASTIRR_API_KEY`
- `OPENAI_API_KEY`

The benchmark also supports optional built-in preset overrides:

- `BASTIRR_GPT5_MODEL`
- `BASTIRR_DEEPSEEK_MODEL`
- `BASTIRR_QWEN_OLLAMA_MODEL`
- `BASTIRR_OLLAMA_API_BASE`
- `DEEPSEEK_API_KEY`
- `DEEPSEEK_API_HOST`

Example Ollama setup using the OpenAI-compatible path:

```bash
OPENAI_API_KEY=ollama
BASTIRR_MODEL_BACKEND=openai
BASTIRR_MODEL=qwen3.5:27b-bf16
BASTIRR_API_BASE=http://localhost:11434/v1
```

## CLI

Main command:

```bash
PYTHONPATH=. python3 -m bastirr.run_screening_benchmark [OPTIONS]
```

Important options:

- `--suite SUITE`
- `--reviews KEY [KEY ...]`
- `--model-presets PRESET [PRESET ...]`
- `--repeats N`
- `--orchestrator-policy fixed|match-gatekeeper`
- `--orchestrator-model PRESET`
- `--gold-label-policy include_label_0_5|exclude_label_0_5`
- `--hide-subagent-steps`
- `--list-suites`
- `--list-model-presets`
- `--list-reviews`

Common examples:

```bash
# GPT-5 smoke test on the 10-study review
PYTHONPATH=. python3 -m bastirr.run_screening_benchmark \
  --model-presets openai_gpt5 \
  --orchestrator-policy fixed \
  --orchestrator-model openai_gpt5 \
  --reviews stroke_theophylline_10

# Run every model in the default screening ladder, 5 times each
PYTHONPATH=. python3 -m bastirr.run_screening_benchmark \
  --repeats 5

# Match the thin orchestrator model to the Gatekeeper model
PYTHONPATH=. python3 -m bastirr.run_screening_benchmark \
  --model-presets openai_gpt5 deepseek_v3_2_thinking \
  --orchestrator-policy match-gatekeeper \
  --repeats 5

# Restrict to a subset of reviews for a quicker sweep
PYTHONPATH=. python3 -m bastirr.run_screening_benchmark \
  --reviews stroke_theophylline_10 alopecia_areata_25 \
  --model-presets openai_gpt5 \
  --repeats 5

# Rescore the same style of runs with label `0.5` treated as `EXCLUDE`
PYTHONPATH=. python3 -m bastirr.run_screening_benchmark \
  --model-presets openai_gpt5 \
  --gold-label-policy exclude_label_0_5 \
  --repeats 5
```

## Orchestrator Policies

Two execution policies are supported:

- `fixed`: the orchestrator model stays constant across the matrix
- `match-gatekeeper`: the orchestrator uses the same preset as the Gatekeeper

The intended default benchmark mode is `fixed`, because the benchmark focus is
screening quality and we usually want the Gatekeeper to be the only changing
LLM in the matrix.

## Output Layout

Experiment outputs live under:

```text
bastirr/output/screening_benchmarks/<timestamp>_<suite>/
```

Inside each experiment directory:

- `summary.json`
- `summary.csv`
- `leaderboard.md`
- `review_leaderboard.md`
- `runs/`

Inside each run directory:

- `workflow.log`
- `activity.md`
- `evidence.json`
- `metrics.json`
- `screening_inspection.json`
- `screening_inspection.md`

## Per-Run Artifacts

### `evidence.json`

Screening-only machine-readable output:

```json
{
  "screening_decisions": [
    {
      "study_index": 1,
      "decision": "INCLUDE",
      "reason": "..."
    }
  ]
}
```

This file is intentionally minimal. It reflects what the screening phase
actually produced, without fake placeholders from Miner or Critic.

The save tool validates completeness when an expected study count is provided.
If the parsed decision list is partial, it raises instead of writing a
misleading `evidence.json`.

### `metrics.json`

Contains:

- confusion counts: `tp`, `fp`, `tn`, `fn`
- `accuracy`, `precision`, `recall`, `specificity`, `f1`
- decision coverage and parse completeness
- completion metadata:
  - `run_status`: `completed`, `incomplete`, or `error`
  - `screening_completion_status`: `complete`, `partial`, or `none`
  - `screening_attempt_count`
  - `rerun_triggered`
  - `scored_for_aggregate`
  - `incomplete_reason`
- timing and model metadata
- paths to the inspection artifacts

Important: benchmark leaderboards average metrics only over runs where
`scored_for_aggregate=true`, meaning the run produced a complete valid
per-study decision list.

### `screening_inspection.json`

The detailed comparison artifact for one run. It includes:

- review title
- review URL
- `screening_criteria`
- gold screening policy
- summary counts
- one entry per study with:
  - `study_index`
  - `study_title`
  - `gold_label`
  - `gold_screening_decision`
  - `gold_review_outcome`
  - `predicted_decision`
  - `predicted_reason`
  - `prediction_matches_gold`
  - `match_status`

This is the best artifact for deterministic downstream analysis or custom
visualization.

### `screening_inspection.md`

A human-readable version of the same inspection data. It surfaces:

- screening criteria
- match, mismatch, and missing-decision counts
- a mismatch table for quick review
- an all-studies table for full auditability

This is the best artifact when manually reading one run.

## Experiment-Level Artifacts

### `summary.json`

Full machine-readable experiment output:

- selected suite
- selected review keys
- selected model presets
- repeats
- gold label policy
- per-run metrics rows
- aggregated model-level leaderboard rows
- aggregated review-level leaderboard rows

### `summary.csv`

Flat row-per-run export of the run metrics. Useful for spreadsheet work or
lightweight analysis.

### `leaderboard.md`

Aggregated benchmark summary grouped by:

- Gatekeeper model label
- Gatekeeper backend and API base
- orchestrator policy
- orchestrator model label
- orchestrator backend and API base

This is where the resolved model names matter. The artifact is meant to stay
readable even as more variants are added later.

The header also records the active gold label policy so model averages are not
read out of context. It also shows how many runs were:

- scored
- incomplete
- errors

so incomplete screening outputs cannot be mistaken for normal benchmark scores.

### `review_leaderboard.md`

Review-centered comparison grouped by review. For each benchmark review it
shows:

- review title and URL
- study count and gold pass/exclude totals
- one ranked row per model configuration

This is usually the more informative artifact when the suite is still small,
because it makes model tradeoffs visible on each specific review rather than
only through one overall average.

Its header also records the active gold label policy, and its per-review rows
also separate scored, incomplete, and error runs.

## Validation Workflow

Recommended local validation after changing the benchmark harness:

```bash
venv/bin/python -m unittest discover -s tests -v
venv/bin/python -m compileall bastirr tests
PYTHONPATH=. python3 -m bastirr.run_screening_benchmark --list-model-presets
PYTHONPATH=. python3 -m bastirr.run_screening_benchmark --list-reviews
```

If the runtime behavior changed, also run a smoke benchmark on the 10-study
review with GPT-5:

```bash
PYTHONPATH=. python3 -m bastirr.run_screening_benchmark \
  --model-presets openai_gpt5 \
  --orchestrator-policy fixed \
  --orchestrator-model openai_gpt5 \
  --reviews stroke_theophylline_10
```

Then inspect:

- `evidence.json`
- `metrics.json`
- `screening_inspection.md`
- `activity.md`
- `workflow.log`

## Notes And Boundaries

- The benchmark does not modify the live 5-agent demo path.
- The thin screening Orchestrator is deliberately limited to retrieval plus
  screening coordination.
- The benchmark writes gold comparison artifacts programmatically after the
  agent run; the agent is not asked to reproduce gold metadata.
- The benchmark is meant for branch-local experimentation and may never merge
  into the main README or mainline runtime story.
