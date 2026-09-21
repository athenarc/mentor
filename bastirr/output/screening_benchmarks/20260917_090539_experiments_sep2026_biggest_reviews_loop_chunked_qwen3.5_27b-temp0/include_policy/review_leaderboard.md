# Review-Level Screening Benchmark Leaderboard

This file compares model configurations within each review.

Gold label policy: `include_label_0_5`

## 14651858_cd011737_pub3

**Title:** Reduction in saturated fat intake for cardiovascular disease
**URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD011737.pub3/full
**Studies:** 558 | **Gold pass:** 487 | **Gold exclude:** 71

Metrics below are averaged only over scored runs with complete per-study decision coverage.

| Rank | Architecture | Gatekeeper Model | Orchestrator Policy | Orchestrator Model | Runs | Scored | Incomplete | Errors | F1 | Recall | Precision | Accuracy | Specificity | Parse Success | Coverage |
|------|--------------|------------------|---------------------|--------------------|------|--------|------------|--------|----|--------|-----------|----------|-------------|---------------|----------|
| 1 | loop_chunk_orchestrator_v1 | qwen3.5_27b-temp0 [Qwen 3.5 27B (temperature 0)] | match-gatekeeper | qwen3.5_27b-temp0 [Qwen 3.5 27B (temperature 0)] | 3 | 3 | 0 | 0 | 0.157 | 0.092 | 1.000 | 0.208 | 1.000 | 1.000 | 1.000 |
