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

Both the review suites and the model presets are file-backed so they can
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
13. After each completed review run, the harness checkpoints policy-local
    `runs/`, `summary.json`, `summary.csv`, and leaderboard files to the
    permanent experiment directory.
14. After scoring, the harness generates policy-local notebooks and
    policy-local HTML summary reports.
15. When both policy folders are present, it also generates a top-level
    policy-comparison HTML report at the experiment root.

## Looped Screening Benchmark

The batch benchmark remains available through:

```bash
venv/bin/python -m bastirr.run_screening_benchmark
```

The looped benchmark is a separate architecture available through:

```bash
venv/bin/python -m bastirr.run_screening_loop_benchmark
```

The looped path uses the same review suites, model presets, scoring policies,
inspection artifacts, notebooks, and HTML reports, but changes the raw agent
run topology:

- the Orchestrator receives protocol context and study indices only
- each candidate is retrieved through a one-study, label-free tool call
- Gatekeeper receives exactly one title/abstract at a time
- each decision is appended immediately to `evidence.json`
- `screening_progress.json` tracks partial progress for retry/resume attempts

Looped runs are marked with:

```text
benchmark_architecture = loop_orchestrator_v1
```

Looped experiment directories include the model key for single-model runs:

```text
bastirr/output/screening_benchmarks/<timestamp>_<suite>_loop_<model_key>/
```

For multi-model loop runs, the suffix is bounded as `modelsN`, for example
`<timestamp>_<suite>_loop_models3/`.

To run only one review from a suite, pass the review key with `--reviews`:

```bash
venv/bin/python -m bastirr.run_screening_loop_benchmark \
  --suite screening_ladder \
  --reviews heart_failure_mhealth_200 \
  --model-presets deepseek_v4_pro \
  --orchestrator-policy fixed \
  --orchestrator-model deepseek_v4_pro \
  --repeats 1
```

This creates a new single-review experiment and refreshes aggregate totals
unless `--skip-totals-aggregation` is supplied.

To replace a failed review inside an existing loop experiment, use
`--rerun-in-experiment` with `--reviews`:

```bash
venv/bin/python -m bastirr.run_screening_loop_benchmark \
  --rerun-in-experiment bastirr/output/screening_benchmarks/20260610_023357_screening_ladder_loop_deepseek_v4_pro \
  --reviews heart_failure_mhealth_200 \
  --skip-policy-notebook-execution \
  --canonical auto
```

Batch experiments use the same in-place rerun shape:

```bash
venv/bin/python -m bastirr.run_screening_benchmark \
  --rerun-in-experiment bastirr/output/screening_benchmarks/<timestamp>_<suite> \
  --reviews adhesive_capsulitis_50 \
  --skip-policy-notebook-execution \
  --canonical auto \
  --orchestrator-max-steps 30
```

The in-place rerun reuses the experiment's original suite, model preset,
orchestrator policy, repeats, and gold-label policies. It reruns only the
selected review key, replaces that run in the policy views, rewrites
`summary.json`, `summary.csv`, leaderboards, HTML reports, and the checkpoint
manifest, and then refreshes aggregate totals unless skipped.

Batch runs are marked as:

```text
benchmark_architecture = batch_orchestrator_v1
```

Aggregate totals keep these architectures separate by default.

### Mini-Batch Loop Mode

For copyable run commands, see `bastirr/benchmarking/CHUNKED_LOOP_RUNS.md`.

The loop CLI also supports a bounded mini-batch mode:

```bash
venv/bin/python -m bastirr.run_screening_loop_benchmark \
  --suite screening_ladder \
  --model-presets deepseek_v4_pro \
  --orchestrator-policy fixed \
  --orchestrator-model deepseek_v4_pro \
  --repeats 1 \
  --loop-mode chunked
```

Chunked mode is still an agent workflow:

```text
Benchmark runner chooses chunk indices
Orchestrator retrieves one chunk through get_candidate_studies_chunk_json()
Orchestrator delegates that chunk to Gatekeeper
Orchestrator appends the validated chunk through append_screening_chunk_decisions_json()
```

The deterministic runner controls only chunk scheduling, checkpointing, and
metrics. It does not classify studies and does not bypass the Orchestrator or
Gatekeeper. Chunked runs are marked with:

```text
benchmark_architecture = loop_chunk_orchestrator_v1
```

Chunked experiment folders use:

```text
bastirr/output/screening_benchmarks/<timestamp>_<suite>_loop_chunked_<model_key>/
```

Default chunk scheduling:

- up to 25 studies: 1 chunk
- 26-50 studies: 2 chunks
- 51-100 studies: 4 chunks
- 101-150 studies: 5 chunks
- 151-225 studies: 6 chunks
- above 225 studies: about 40 studies per chunk

You can override this with either `--chunk-count N` or `--chunk-size N`.
Use only one override at a time.

## Components

Key files:

- `bastirr/run_screening_benchmark.py`
- `bastirr/run_screening_loop_benchmark.py`
- `bastirr/agents/screening_orchestrator.py`
- `bastirr/agents/screening_loop_orchestrator.py`
- `bastirr/tools/screening_benchmark_tools.py`
- `bastirr/benchmarking/loop_runner.py`
- `bastirr/benchmarking/review_suites.py`
- `bastirr/benchmarking/model_presets.py`
- `bastirr/benchmarking/metrics.py`
- `bastirr/benchmarking/telemetry.py`
- `bastirr/benchmarking/totals.py`
- `bastirr/benchmarking/inspection.py`
- `bastirr/benchmarking/notebooks.py`
- `bastirr/benchmarking/html_reports.py`
- `bastirr/benchmarking/comparison_reports.py`
- `bastirr/benchmarking/runner.py`
- `bastirr/generate_screening_html_report.py`

Responsibilities:

- `screening_orchestrator.py`: thin manager that does retrieval plus
  Gatekeeper delegation only, and is explicitly forbidden from reconstructing
  screening decisions itself
- `screening_benchmark_tools.py`: screening-only persistence and short summary
- `review_suites.py`: locked benchmark review registries
- `model_presets.py`: named Gatekeeper and orchestrator model presets
- `metrics.py`: gold-label mapping and study-level metrics
- `inspection.py`: study-by-study gold-vs-prediction comparison artifacts
- `notebooks.py`: policy-local exploratory notebook generation
- `html_reports.py`: policy-local HTML summary report generation
- `comparison_reports.py`: experiment-level side-by-side policy comparison report generation
- `runner.py`: experiment loop, logging, metrics, summaries, output layout,
  and artifact generation

## Gold Label Policies

The benchmark treats gold-label interpretation as a scoring lens rather
than a run-time setting for the agents.

The raw screening run happens once per review/model/repeat configuration, and
the saved Gatekeeper decisions are then scored under both policies by default.
This means the agent outputs do not change across policies; only the metric and
inspection interpretation changes.

Underlying dataset labels mean:

- `1.0`: included in the final review
- `0.5`: passed title/abstract screening but was excluded later
- `0.0`: excluded at screening

The inspection artifacts preserve those review-level meanings directly:

- `included_in_review`
- `excluded_after_full_text`
- `excluded_at_screening`

By default, each benchmark experiment materializes both scoring policies from
the same saved screening outputs:

- `include_label_0_5`: screening-oriented lens where `1.0` and `0.5` count as
  `INCLUDE`, and only `0.0` counts as `EXCLUDE`
- `exclude_label_0_5`: stricter lens where only `1.0` counts as `INCLUDE`, and
  both `0.5` and `0.0` count as `EXCLUDE`

That is why a benchmark folder contains sibling `include_policy/` and
`exclude_policy/` directories when both are generated.

Benchmark run commands always materialize both policy views. To choose which
policy is used for aggregate canonical totals, use
`bastirr.recompute_screening_totals --canonical-policy ...`.

## Locked Review Suite

The default suite is `screening_ladder`. It is a fixed ladder of escalating
review sizes, and the same underlying review bundle is reused for both gold
label policies.

Because the benchmark scores both policies by default, the most useful way
to read the suite is:

- `final_include_count`: studies with dataset label `1.0`
- `pass_to_full_text_count`: studies with dataset label `0.5`
- `screen_exclude_count`: studies with dataset label `0.0`

From those underlying counts:

- `include_label_0_5` treats `final_include_count + pass_to_full_text_count`
  as gold `INCLUDE`
- `exclude_label_0_5` treats only `final_include_count` as gold `INCLUDE`

| Key | Split | Studies | Final Include (`1.0`) | Passed To Full Text (`0.5`) | Excluded At Screening (`0.0`) |
|-----|-------|---------|------------------------|------------------------------|--------------------------------|
| `stroke_theophylline_10` | `val` | 10 | 2 | 4 | 4 |
| `alopecia_areata_25` | `random_test` | 25 | 13 | 4 | 8 |
| `iud_insertion_pain_50` | `random_test` | 50 | 26 | 4 | 20 |
| `pelvic_floor_training_100` | `random_test` | 100 | 26 | 22 | 52 |
| `heart_failure_mhealth_200` | `heart_test` | 200 | 4 | 133 | 63 |

The benchmark also includes `screening_ladder_dev_exclude_balanced`, a
dev-only five-review ladder selected so that `exclude_label_0_5` stays within
a more reasonable class balance at every size point. The largest review in that
suite is slightly smaller (`194` studies instead of `200`) because the
available dev-set candidates become extremely imbalanced under the stricter
policy beyond that point.

Its underlying dataset counts are:

| Key | Split | Studies | Final Include (`1.0`) | Passed To Full Text (`0.5`) | Excluded At Screening (`0.0`) |
|-----|-------|---------|------------------------|------------------------------|--------------------------------|
| `endometrial_progestagens_10` | `dev` | 10 | 5 | 0 | 5 |
| `tricyclic_depression_children_25` | `dev` | 25 | 12 | 3 | 10 |
| `adhesive_capsulitis_50` | `dev` | 50 | 25 | 6 | 19 |
| `desmopressin_transfusion_100` | `dev` | 100 | 54 | 18 | 28 |
| `prom_feedback_194` | `dev` | 194 | 98 | 50 | 46 |

The benchmark also includes `screening_ladder_dev_no_label_0_5`, a dev-only
five-review ladder composed entirely of reviews whose dataset labels contain no
`0.5` studies. Under that suite, `include_label_0_5` and
`exclude_label_0_5` score the same underlying gold labels, which makes it
useful for isolating benchmark behavior in reviews without full-text-screening
exclusions.

Its underlying dataset counts are:

| Key | Split | Studies | Final Include (`1.0`) | Passed To Full Text (`0.5`) | Excluded At Screening (`0.0`) |
|-----|-------|---------|------------------------|------------------------------|--------------------------------|
| `surgical_termination_10` | `dev` | 10 | 7 | 0 | 3 |
| `advanced_endometrial_carcinoma_24` | `dev` | 24 | 12 | 0 | 12 |
| `chlamydia_poc_test_50` | `dev` | 50 | 19 | 0 | 31 |
| `ovarian_cancer_diagnosis_92` | `dev` | 92 | 45 | 0 | 47 |
| `home_based_rehabilitation_183` | `dev` | 183 | 138 | 0 | 45 |

The suite definitions live in
`bastirr/benchmarking/config/review_suites.json`.

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
- `deepseek_v4_pro`
- `ollama_qwen3_5_27b_bf16`

Current meanings:

- `openai_gpt5`: GPT-5 benchmark preset, now called through OpenRouter
- `deepseek_v4_pro`: DeepSeek V4 Pro benchmark preset, now called through OpenRouter
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

The generic Bastirr model configuration remains useful for
single-model runs:

- `BASTIRR_MODEL_BACKEND`
- `BASTIRR_MODEL`
- `BASTIRR_API_BASE`
- `BASTIRR_API_KEY`
- `OPENAI_API_KEY`

The benchmark also supports optional built-in preset overrides:

- `OPENROUTER_API_KEY`
- `OPENROUTER_API_BASE`
- `BASTIRR_GPT5_MODEL`
- `BASTIRR_DEEPSEEK_MODEL`
- `BASTIRR_QWEN_OLLAMA_MODEL`
- `BASTIRR_OLLAMA_API_BASE`

Recommended OpenRouter setup for the benchmark presets:

```bash
OPENROUTER_API_KEY=sk-or-v1-...
OPENROUTER_API_BASE=https://openrouter.ai/api/v1

# Optional explicit preset overrides
BASTIRR_GPT5_MODEL=openai/gpt-5
BASTIRR_DEEPSEEK_MODEL=deepseek/deepseek-v4-pro
```

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
- `--skip-policy-notebook-execution`
- `--hide-subagent-steps`
- `--canonical auto|none|force`
- `--orchestrator-max-steps N`
- `--rerun-in-experiment PATH`
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
  --reviews stroke_theophylline_10 \
  --canonical auto

# Run every model in the default screening ladder, 5 times each
PYTHONPATH=. python3 -m bastirr.run_screening_benchmark \
  --repeats 5 \
  --canonical none

# Run GPT-5 on the dev-only ladder that stays better balanced under
# exclude_label_0_5
PYTHONPATH=. python3 -m bastirr.run_screening_benchmark \
  --suite screening_ladder_dev_exclude_balanced \
  --model-presets openai_gpt5 \
  --orchestrator-policy fixed \
  --orchestrator-model openai_gpt5 \
  --repeats 5 \
  --canonical none

# Run GPT-5 on the dev-only ladder with no 0.5 labels anywhere in the suite
PYTHONPATH=. python3 -m bastirr.run_screening_benchmark \
  --suite screening_ladder_dev_no_label_0_5 \
  --model-presets openai_gpt5 \
  --orchestrator-policy fixed \
  --orchestrator-model openai_gpt5 \
  --repeats 5 \
  --canonical none

# Match the thin orchestrator model to the Gatekeeper model
PYTHONPATH=. python3 -m bastirr.run_screening_benchmark \
  --model-presets openai_gpt5 deepseek_v4_pro \
  --orchestrator-policy match-gatekeeper \
  --repeats 5 \
  --canonical none

# Restrict to a subset of reviews for a quicker sweep
PYTHONPATH=. python3 -m bastirr.run_screening_benchmark \
  --reviews stroke_theophylline_10 alopecia_areata_25 \
  --model-presets openai_gpt5 \
  --repeats 5 \
  --canonical none

# Write both policy views from the same raw screening runs
PYTHONPATH=. python3 -m bastirr.run_screening_benchmark \
  --model-presets openai_gpt5 \
  --repeats 5 \
  --canonical none
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

- `include_policy/`
- `exclude_policy/`

The experiment root is intentionally minimal. It acts as the parent container
for the policy-specific views rather than storing benchmark outputs itself.
Raw agent artifacts such as `workflow.log`, `activity.md`, and `evidence.json`
are copied into each policy-specific run directory so every policy view is
self-contained.

The benchmark also maintains checkpoint artifacts at the experiment root:

- `_raw_runs/`: persistent raw agent run directories, including any looped
  `evidence.json` and `screening_progress.json` written while a review is in
  progress
- `benchmark_checkpoint.json`: machine-readable checkpoint manifest with the
  number of completed raw runs, expected raw runs, policy output paths, and
  raw run directories

Policy folders are refreshed after every completed review run. If a later
large review stalls or the process is terminated, the completed earlier runs
remain available under each policy folder and in `_raw_runs/`.

Each policy directory contains policy-specific derived artifacts:

- `runs/`
- `summary.json`
- `summary.csv`
- `leaderboard.md`
- `review_leaderboard.md`
- `screening_results_analysis.ipynb`

Inside each policy run directory:

- `workflow.log`
- `activity.md`
- `evidence.json`
- `metrics.json`
- `screening_progress.json` for looped runs
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
- benchmark architecture metadata
- workflow telemetry:
  - input/output/total tokens
  - total and per-agent step counts
  - error, retry, and resume counts
  - duration per study
- rationale shortcut indicators:
  - empty rationale count
  - duplicate rationale count
  - rationale reuse rate
- paths to the inspection artifacts

Important: benchmark leaderboards average metrics only over runs where
`scored_for_aggregate=true`, meaning the run produced a complete valid
per-study decision list.

### `screening_progress.json`

Looped runs write a progress artifact alongside `evidence.json`:

```json
{
  "expected_n_studies": 10,
  "completed_count": 4,
  "completed_study_indices": [1, 2, 3, 4],
  "next_study_index": 5,
  "screening_decisions": []
}
```

This file lets a retry continue from missing studies instead of replacing
already saved decisions.

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

### Policy `summary.json`

Full machine-readable scoring output for one gold-label policy:

- active gold label policy
- per-run metrics rows
- aggregated model-level leaderboard rows
- aggregated review-level leaderboard rows

At the parent experiment level, the runtime summary also records:

- the generated policy folders
- policy-local notebook paths
- policy-local HTML report paths
- the comparison HTML report path when both policies are present

### `summary.csv`

Flat row-per-run export for one gold-label policy. Useful for spreadsheet work
or lightweight analysis.

### `screening_results_analysis.ipynb`

Policy-local exploratory notebook generated from that folder's own
`summary.csv`, `summary.json`, and `runs/` tree. It does not compare against
the alternate policy. Instead it focuses on:

- run completeness and coverage
- metric stability across repeats
- review-level performance patterns
- pass-count calibration
- repeated study-level mismatches

The benchmark generates this notebook automatically for each policy folder.
By default it also tries to pre-execute the notebook so plots are already
rendered. If you want only the notebook file without execution, use
`--skip-policy-notebook-execution`. Notebook execution is best-effort: if the
local Jupyter kernel cannot be launched, the `.ipynb` file is written and
can be opened or executed later.

### `screening_results_summary.html`

Policy-local visual summary report generated from that folder's own
`summary.csv`, `summary.json`, and per-run inspection artifacts.

It is a presentation-style benchmark overview rather than an exploratory
notebook. The report highlights:

- run health and pooled macro metrics
- pooled confusion totals
- review-level performance and runtime
- repeat-to-repeat stability across scored runs
- recurring study-level mistakes

The report is generated automatically for each policy folder during both normal
benchmark runs and benchmark backfills.

The report intentionally links only to browser-friendly artifacts such as
`summary.csv`, `summary.json`, and sibling HTML reports. The notebook remains a
filesystem artifact in the policy folder, but it is not linked from the HTML
report because raw `.ipynb` files do not render well in a normal browser.

You can also regenerate HTML reports manually:

```bash
venv/bin/python -m bastirr.generate_screening_html_report \
  bastirr/output/screening_benchmarks/20260409_000456_screening_ladder/include_policy
```

Or point it at the parent benchmark directory to regenerate all policy reports:

```bash
venv/bin/python -m bastirr.generate_screening_html_report \
  bastirr/output/screening_benchmarks/20260409_000456_screening_ladder
```

When you point the command at the parent benchmark directory, it also generates
the top-level comparison report:

### `screening_policy_comparison.html`

Experiment-level side-by-side report that compares the `include_policy` and
`exclude_policy` views created from the same saved screening runs. It focuses
on:

- side-by-side policy cards
- recall and F1 movement by review
- error composition under each policy
- review-by-review metric comparison

It intentionally does not repeat the full study-level detail from the
individual policy reports. Use the policy-local reports when you need:

- pooled confusion totals for one policy
- repeat variability within one policy
- recurring study-level mistakes within one policy

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

This is usually the more informative artifact when the suite is small,
because it makes model tradeoffs visible on each specific review rather than
only through one overall average.

Its header also records the active gold label policy, and its per-review rows
also separate scored, incomplete, and error runs.

### Aggregate totals

Both benchmark CLIs refresh aggregate totals after a completed run unless
`--skip-totals-aggregation` is supplied. Normal runs also update the canonical
source manifest before totals are recomputed:

```text
bastirr/output/screening_benchmarks/totals/canonical_sources.json
```

The manifest is keyed by suite, gold-label policy, benchmark architecture,
review key, Gatekeeper preset, Orchestrator policy, and Orchestrator preset.
Provider/API base is not part of model identity. By default, only completed and
scored `repeats=1` runs are registered, and experiment folders whose names
contain `_repN` are excluded from canonical seeding/auto-registration. Use
`--canonical none` for calibration or debug runs, and `--canonical force` only
when a repeated run should replace the canonical pointer.

For manual validation, canonical seeding also writes:

```text
bastirr/output/screening_benchmarks/totals/canonical_sources_audit.md
```

This audit view groups selections by suite, policy, architecture, Gatekeeper
preset, and selected source experiment directory, so it is easier to check that
a model/suite points to the intended timestamped run folder.

Totals are written under:

```text
bastirr/output/screening_benchmarks/totals/<suite>/<policy>/<architecture>/
```

To seed or inspect the canonical manifest without rewriting aggregate totals:

```bash
venv/bin/python -m bastirr.recompute_screening_totals --build-canonical-only
```

Totals can also be recomputed without running a benchmark. The default source
mode is `canonical`, so it reads only `canonical_sources.json`:

```bash
venv/bin/python -m bastirr.recompute_screening_totals
```

For audits, the older discovery behavior is still available:

```bash
venv/bin/python -m bastirr.recompute_screening_totals --source-mode discover
```

Each architecture-separated totals folder contains:

- `totals_leaderboard.json`
- `totals_leaderboard.md`
- `totals_review_leaderboard.json`
- `totals_review_leaderboard.md`
- `per_sr/<review_key>_leaderboard.json`
- `per_sr/<review_key>_leaderboard.md`

Horizontal size-band comparisons are pooled across suites and written under:

```text
bastirr/output/screening_benchmarks/totals/horizontal_comparison/<policy>/<architecture>/
```

Each horizontal comparison folder contains:

- `horizontal_size_bands.json`
- `horizontal_size_bands.md`

The horizontal size bands are:

- `small_10`: up to 15 studies
- `lower_mid_25`: 16-35 studies
- `mid_50`: 36-65 studies
- `upper_mid_100`: 66-100 studies
- `large_100_plus`: greater than 100 studies, displayed as `100+`

## Validation Workflow

Recommended local validation after changing the benchmark harness:

```bash
venv/bin/python -m unittest discover -s tests -v
venv/bin/python -m compileall bastirr tests
venv/bin/python -m bastirr.run_screening_benchmark --list-model-presets
venv/bin/python -m bastirr.run_screening_benchmark --list-reviews
venv/bin/python -m bastirr.run_screening_loop_benchmark --list-reviews
```

If the runtime behavior changed, also run a smoke benchmark on the 10-study
review with GPT-5:

```bash
venv/bin/python -m bastirr.run_screening_benchmark \
  --model-presets openai_gpt5 \
  --orchestrator-policy fixed \
  --orchestrator-model openai_gpt5 \
  --reviews stroke_theophylline_10 \
  --canonical auto
```

Then inspect:

- `evidence.json`
- `metrics.json`
- `screening_inspection.md`
- `activity.md`
- `workflow.log`

## Legacy Backfill

Older flat benchmark directories can be restructured into the current
policy-owned layout without rerunning any models:

```bash
venv/bin/python -m bastirr.backfill_screening_benchmark \
  bastirr/output/screening_benchmarks/<timestamp>_<suite>
```

To backfill the policy folders but leave the notebooks unexecuted:

```bash
venv/bin/python -m bastirr.backfill_screening_benchmark \
  bastirr/output/screening_benchmarks/<timestamp>_<suite> \
  --skip-policy-notebook-execution
```

## Notes And Boundaries

- The benchmark does not modify the live 5-agent demo path.
- The thin screening Orchestrator is deliberately limited to retrieval plus
  screening coordination.
- The benchmark writes gold comparison artifacts programmatically after the
  agent run; the agent is not asked to reproduce gold metadata.
- The benchmark is meant for branch-local experimentation and may never merge
  into the main README or mainline runtime story.
