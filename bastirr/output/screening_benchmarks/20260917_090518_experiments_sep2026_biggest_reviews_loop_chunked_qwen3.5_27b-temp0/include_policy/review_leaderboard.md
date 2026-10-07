# Review-Level Screening Benchmark Leaderboard

This file compares model configurations within each review.

Gold label policy: `include_label_0_5`

## 14651858_cd011901_pub2

**Title:** Visual inspection and dermoscopy, alone or in combination, for diagnosing keratinocyte skin cancers in adults
**URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD011901.pub2/full
**Studies:** 470 | **Gold pass:** 383 | **Gold exclude:** 87

Metrics below are averaged only over scored runs with complete per-study decision coverage.

| Rank | Architecture | Gatekeeper Model | Orchestrator Policy | Orchestrator Model | Runs | Scored | Incomplete | Errors | F1 | Recall | Precision | Accuracy | Specificity | Parse Success | Coverage |
|------|--------------|------------------|---------------------|--------------------|------|--------|------------|--------|----|--------|-----------|----------|-------------|---------------|----------|
| 1 | loop_chunk_orchestrator_v1 | qwen3.5_27b-temp0 [Qwen 3.5 27B (temperature 0)] | match-gatekeeper | qwen3.5_27b-temp0 [Qwen 3.5 27B (temperature 0)] | 3 | 1 | 1 | 1 | 0.396 | 0.256 | 0.875 | 0.364 | 0.839 | 0.333 | 0.475 |
