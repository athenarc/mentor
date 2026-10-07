# Review-Level Screening Benchmark Leaderboard

This file compares model configurations within each review.

Gold label policy: `exclude_label_0_5`

## 14651858_cd011834

**Title:** Effects of total fat intake on body weight
**URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD011834/full
**Studies:** 409 | **Gold pass:** 7 | **Gold exclude:** 402

Metrics below are averaged only over scored runs with complete per-study decision coverage.

| Rank | Architecture | Gatekeeper Model | Orchestrator Policy | Orchestrator Model | Runs | Scored | Incomplete | Errors | F1 | Recall | Precision | Accuracy | Specificity | Parse Success | Coverage |
|------|--------------|------------------|---------------------|--------------------|------|--------|------------|--------|----|--------|-----------|----------|-------------|---------------|----------|
| 1 | loop_chunk_orchestrator_v1 | qwen3.5_27b-temp0 [Qwen 3.5 27B (temperature 0)] | match-gatekeeper | qwen3.5_27b-temp0 [Qwen 3.5 27B (temperature 0)] | 3 | 1 | 2 | 0 | n/a | 0.000 | 0.000 | 0.932 | 0.948 | 0.333 | 0.667 |
