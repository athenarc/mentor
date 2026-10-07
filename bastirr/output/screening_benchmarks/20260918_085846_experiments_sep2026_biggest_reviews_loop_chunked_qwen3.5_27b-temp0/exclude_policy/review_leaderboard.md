# Review-Level Screening Benchmark Leaderboard

This file compares model configurations within each review.

Gold label policy: `exclude_label_0_5`

## 14651858_cd012599

**Title:** First and second trimester serum tests with and without first trimester ultrasound tests for Down's syndrome screening
**URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD012599/full
**Studies:** 497 | **Gold pass:** 19 | **Gold exclude:** 478

Metrics below are averaged only over scored runs with complete per-study decision coverage.

| Rank | Architecture | Gatekeeper Model | Orchestrator Policy | Orchestrator Model | Runs | Scored | Incomplete | Errors | F1 | Recall | Precision | Accuracy | Specificity | Parse Success | Coverage |
|------|--------------|------------------|---------------------|--------------------|------|--------|------------|--------|----|--------|-----------|----------|-------------|---------------|----------|
| 1 | loop_chunk_orchestrator_v1 | qwen3.5_27b-temp0 [Qwen 3.5 27B (temperature 0)] | match-gatekeeper | qwen3.5_27b-temp0 [Qwen 3.5 27B (temperature 0)] | 3 | 2 | 0 | 1 | 0.473 | 0.684 | 0.361 | 0.942 | 0.952 | 0.667 | 0.667 |
