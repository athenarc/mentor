# Review-Level Screening Benchmark Leaderboard

This file compares model configurations within each review.

Gold label policy: `exclude_label_0_5`

## 14651858_cd012600

**Title:** First trimester ultrasound tests alone or in combination with first trimester serum tests for Down's syndrome screening
**URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD012600/full
**Studies:** 671 | **Gold pass:** 114 | **Gold exclude:** 557

Metrics below are averaged only over scored runs with complete per-study decision coverage.

| Rank | Architecture | Gatekeeper Model | Orchestrator Policy | Orchestrator Model | Runs | Scored | Incomplete | Errors | F1 | Recall | Precision | Accuracy | Specificity | Parse Success | Coverage |
|------|--------------|------------------|---------------------|--------------------|------|--------|------------|--------|----|--------|-----------|----------|-------------|---------------|----------|
| 1 | loop_chunk_orchestrator_v1 | qwen3.5_27b-temp0 [Qwen 3.5 27B (temperature 0)] | match-gatekeeper | qwen3.5_27b-temp0 [Qwen 3.5 27B (temperature 0)] | 3 | 3 | 0 | 0 | 0.521 | 0.836 | 0.379 | 0.739 | 0.719 | 1.000 | 1.000 |
