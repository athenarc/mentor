# Review-Level Screening Benchmark Leaderboard

This file compares model configurations within each review.

Gold label policy: `exclude_label_0_5`

## 14651858_cd011975

**Title:** First trimester serum tests for Down's syndrome screening
**URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD011975/full
**Studies:** 618 | **Gold pass:** 56 | **Gold exclude:** 562

Metrics below are averaged only over scored runs with complete per-study decision coverage.

| Rank | Architecture | Gatekeeper Model | Orchestrator Policy | Orchestrator Model | Runs | Scored | Incomplete | Errors | F1 | Recall | Precision | Accuracy | Specificity | Parse Success | Coverage |
|------|--------------|------------------|---------------------|--------------------|------|--------|------------|--------|----|--------|-----------|----------|-------------|---------------|----------|
| 1 | loop_chunk_orchestrator_v1 | qwen3.5_27b-temp0 [Qwen 3.5 27B (temperature 0)] | match-gatekeeper | qwen3.5_27b-temp0 [Qwen 3.5 27B (temperature 0)] | 3 | 0 | 2 | 1 | n/a | n/a | n/a | n/a | n/a | 0.000 | 0.279 |
