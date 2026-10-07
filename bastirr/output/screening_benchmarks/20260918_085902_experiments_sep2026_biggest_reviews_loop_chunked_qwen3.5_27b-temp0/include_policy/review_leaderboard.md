# Review-Level Screening Benchmark Leaderboard

This file compares model configurations within each review.

Gold label policy: `include_label_0_5`

## 14651858_cd011598_pub2

**Title:** Nutrition support in hospitalised adults at nutritional risk
**URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD011598.pub2/full
**Studies:** 534 | **Gold pass:** 468 | **Gold exclude:** 66

Metrics below are averaged only over scored runs with complete per-study decision coverage.

| Rank | Architecture | Gatekeeper Model | Orchestrator Policy | Orchestrator Model | Runs | Scored | Incomplete | Errors | F1 | Recall | Precision | Accuracy | Specificity | Parse Success | Coverage |
|------|--------------|------------------|---------------------|--------------------|------|--------|------------|--------|----|--------|-----------|----------|-------------|---------------|----------|
| 1 | loop_chunk_orchestrator_v1 | qwen3.5_27b-temp0 [Qwen 3.5 27B (temperature 0)] | match-gatekeeper | qwen3.5_27b-temp0 [Qwen 3.5 27B (temperature 0)] | 3 | 0 | 2 | 1 | n/a | n/a | n/a | n/a | n/a | 0.000 | 0.312 |
