# Chunked Loop Screening Benchmark Runs

Use this runbook for the mini-batch loop architecture:

```text
benchmark_architecture = loop_chunk_orchestrator_v1
```

Chunked loop runs keep the Orchestrator and Gatekeeper agent workflow, but split
each review into bounded study chunks instead of one full-review batch or one
study at a time.

## Standard Full-Suite Run

Use this shape for one model on one suite:

```bash
python3 -m bastirr.run_screening_loop_benchmark \
  --suite screening_ladder_dev_no_label_0_5 \
  --model-presets deepseek_v4_pro \
  --orchestrator-policy fixed \
  --orchestrator-model deepseek_v4_pro \
  --repeats 1 \
  --loop-mode chunked \
  --canonical auto
```

`--canonical auto` registers completed/scored repeat-1 runs into
`totals/canonical_sources.json` and refreshes aggregate totals after the run.

## Run One Review

Use `--reviews` with the review key:

```bash
python3 -m bastirr.run_screening_loop_benchmark \
  --suite screening_ladder_dev_no_label_0_5 \
  --reviews review_key_here \
  --model-presets deepseek_v4_pro \
  --orchestrator-policy fixed \
  --orchestrator-model deepseek_v4_pro \
  --repeats 1 \
  --loop-mode chunked \
  --canonical auto
```

## Rerun One Review In An Existing Experiment

Use this when a previous loop/chunked experiment has one failed or stale review:

```bash
python3 -m bastirr.run_screening_loop_benchmark \
  --rerun-in-experiment bastirr/output/screening_benchmarks/<experiment_dir> \
  --reviews review_key_here \
  --loop-mode chunked \
  --canonical auto
```

The rerun uses the experiment checkpoint for suite, model, repeats, and
orchestrator settings. It replaces only the selected review result and
recomputes both policy summaries/totals.

## Chunk Controls

Default chunk scheduling is size-based:

- up to 25 studies: 1 chunk
- 26-50 studies: 2 chunks
- 51-100 studies: 4 chunks
- 101-150 studies: 5 chunks
- 151-225 studies: 6 chunks
- above 225 studies: about 40 studies per chunk

Override by number of chunks:

```bash
--chunk-count 4
```

Or override by maximum chunk size:

```bash
--chunk-size 25
```

Use only one override at a time.

## Useful Listing Commands

List suites:

```bash
python3 -m bastirr.run_screening_loop_benchmark --list-suites
```

List reviews in a suite:

```bash
python3 -m bastirr.run_screening_loop_benchmark \
  --suite screening_ladder_dev_no_label_0_5 \
  --list-reviews
```

List model presets:

```bash
python3 -m bastirr.run_screening_loop_benchmark --list-model-presets
```

## Notes

- Benchmark runs always write both `include_policy/` and `exclude_policy/`.
- Use `bastirr.recompute_screening_totals --canonical-policy ...` for canonical
  totals selection.
- Use `--canonical none` for exploratory runs that should not update
  `canonical_sources.json`.
- Use `--skip-totals-aggregation` only when you explicitly want to defer totals
  recomputation.
- Add `--skip-policy-notebook-execution` if notebooks are slow or unnecessary
  for a run.
