# Review-Level Screening Benchmark Leaderboard

This file compares model configurations within each review.

Gold label policy: `exclude_label_0_5`

## 14651858_cd002967_pub4

**Title:** Risk of fatal and nonfatal lactic acidosis with metformin use in type 2 diabetes mellitus
**URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD002967.pub4/full
**Studies:** 405 | **Gold pass:** 295 | **Gold exclude:** 110

Metrics below are averaged only over scored runs with complete per-study decision coverage.

| Rank | Architecture | Gatekeeper Model | Orchestrator Policy | Orchestrator Model | Runs | Scored | Incomplete | Errors | F1 | Recall | Precision | Accuracy | Specificity | Parse Success | Coverage |
|------|--------------|------------------|---------------------|--------------------|------|--------|------------|--------|----|--------|-----------|----------|-------------|---------------|----------|
| 1 | loop_chunk_orchestrator_v1 | qwen3.5_27b-temp0 [Qwen 3.5 27B (temperature 0)] | match-gatekeeper | qwen3.5_27b-temp0 [Qwen 3.5 27B (temperature 0)] | 3 | 3 | 0 | 0 | 0.634 | 0.523 | 0.812 | 0.565 | 0.676 | 1.000 | 1.000 |
