# Review-Level Screening Benchmark Leaderboard

This file compares model configurations within each review.

Gold label policy: `exclude_label_0_5`

## 14651858_cd013856_pub2

**Title:** Physical exercise for people with Parkinson’s disease: a systematic review and network meta‐analysis
**URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD013856.pub2/full
**Studies:** 233 | **Gold pass:** 136 | **Gold exclude:** 97

Metrics below are averaged only over scored runs with complete per-study decision coverage.

| Rank | Architecture | Gatekeeper Model | Orchestrator Policy | Orchestrator Model | Runs | Scored | Incomplete | Errors | F1 | Recall | Precision | Accuracy | Specificity | Parse Success | Coverage |
|------|--------------|------------------|---------------------|--------------------|------|--------|------------|--------|----|--------|-----------|----------|-------------|---------------|----------|
| 1 | batch_orchestrator_v1 | qwen3.5_27b-temp0 [Qwen 3.5 27B (temperature 0)] | match-gatekeeper | qwen3.5_27b-temp0 [Qwen 3.5 27B (temperature 0)] | 3 | 3 | 0 | 0 | 0.876 | 0.907 | 0.849 | 0.851 | 0.773 | 1.000 | 1.000 |
