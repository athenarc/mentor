# Review-Level Screening Benchmark Leaderboard

This file compares model configurations within each review.

Gold label policy: `exclude_label_0_5`

## 14651858_cd008944_pub3

**Title:** Early and late adverse renal effects after potentially nephrotoxic treatment for childhood cancer
**URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD008944.pub3/full
**Studies:** 471 | **Gold pass:** 54 | **Gold exclude:** 417

Metrics below are averaged only over scored runs with complete per-study decision coverage.

| Rank | Architecture | Gatekeeper Model | Orchestrator Policy | Orchestrator Model | Runs | Scored | Incomplete | Errors | F1 | Recall | Precision | Accuracy | Specificity | Parse Success | Coverage |
|------|--------------|------------------|---------------------|--------------------|------|--------|------------|--------|----|--------|-----------|----------|-------------|---------------|----------|
| 1 | loop_chunk_orchestrator_v1 | qwen3.5_27b-temp0 [Qwen 3.5 27B (temperature 0)] | match-gatekeeper | qwen3.5_27b-temp0 [Qwen 3.5 27B (temperature 0)] | 3 | 3 | 0 | 0 | 0.465 | 0.895 | 0.317 | 0.757 | 0.739 | 1.000 | 1.000 |
