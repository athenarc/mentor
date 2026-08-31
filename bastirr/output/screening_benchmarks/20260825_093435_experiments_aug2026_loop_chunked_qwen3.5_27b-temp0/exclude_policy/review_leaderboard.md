# Review-Level Screening Benchmark Leaderboard

This file compares model configurations within each review.

Gold label policy: `exclude_label_0_5`

## 14651858_cd001357

**Title:** Amisulpride for schizophrenia
**URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD001357/full
**Studies:** 31 | **Gold pass:** 10 | **Gold exclude:** 21

Metrics below are averaged only over scored runs with complete per-study decision coverage.

| Rank | Architecture | Gatekeeper Model | Orchestrator Policy | Orchestrator Model | Runs | Scored | Incomplete | Errors | F1 | Recall | Precision | Accuracy | Specificity | Parse Success | Coverage |
|------|--------------|------------------|---------------------|--------------------|------|--------|------------|--------|----|--------|-----------|----------|-------------|---------------|----------|
| 1 | loop_chunk_orchestrator_v1 | qwen3.5_27b-temp0 [Qwen 3.5 27B (temperature 0)] | match-gatekeeper | qwen3.5_27b-temp0 [Qwen 3.5 27B (temperature 0)] | 2 | 2 | 0 | 0 | 0.976 | 1.000 | 0.955 | 0.984 | 0.976 | 1.000 | 1.000 |
