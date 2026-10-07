# Review-Level Screening Benchmark Leaderboard

This file compares model configurations within each review.

Gold label policy: `exclude_label_0_5`

## 14651858_cd011535_pub6

**Title:** Systemic pharmacological treatments for chronic plaque psoriasis: a network meta‐analysis
**URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD011535.pub6/full
**Studies:** 440 | **Gold pass:** 86 | **Gold exclude:** 354

Metrics below are averaged only over scored runs with complete per-study decision coverage.

| Rank | Architecture | Gatekeeper Model | Orchestrator Policy | Orchestrator Model | Runs | Scored | Incomplete | Errors | F1 | Recall | Precision | Accuracy | Specificity | Parse Success | Coverage |
|------|--------------|------------------|---------------------|--------------------|------|--------|------------|--------|----|--------|-----------|----------|-------------|---------------|----------|
| 1 | loop_chunk_orchestrator_v1 | qwen3.5_27b-temp0 [Qwen 3.5 27B (temperature 0)] | match-gatekeeper | qwen3.5_27b-temp0 [Qwen 3.5 27B (temperature 0)] | 3 | 2 | 1 | 0 | 0.505 | 0.965 | 0.343 | 0.630 | 0.548 | 0.667 | 0.818 |
