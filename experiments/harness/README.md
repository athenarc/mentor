# Screening harness (analysis)

Execution lives in **`experiments suite`**. This package scores and materializes
policy views from suite experiment directories.

```bash
uv run experiments suite --suite screening_ladder --profiles openai_gpt5 --batch-size 10
uv run experiments analyze data/experiments/output/screening_benchmarks/<suite_dir>
```

Review suites: `experiments/config/suites.json` (via `experiments.suites`).
Dataset / gold labels: `experiments.dataset`.

Derived from `run.json` → `screening_batch_size`:

- omitted / null → all studies in one Gatekeeper call (`batch`)
- `1` → single-study
- `N>1` → chunked

Analyze expects `_raw_runs/<cell>/run.json` + `evidence.json` (`screening_decisions`).
