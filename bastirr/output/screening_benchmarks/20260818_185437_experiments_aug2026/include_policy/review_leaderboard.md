# Review-Level Screening Benchmark Leaderboard

This file compares model configurations within each review.

Gold label policy: `include_label_0_5`

## 14651858_cd010673_pub2

**Title:** Psychological therapies for the treatment of anxiety disorders in chronic obstructive pulmonary disease
**URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD010673.pub2/full
**Studies:** 58 | **Gold pass:** 12 | **Gold exclude:** 46

Metrics below are averaged only over scored runs with complete per-study decision coverage.

| Rank | Architecture | Gatekeeper Model | Orchestrator Policy | Orchestrator Model | Runs | Scored | Incomplete | Errors | F1 | Recall | Precision | Accuracy | Specificity | Parse Success | Coverage |
|------|--------------|------------------|---------------------|--------------------|------|--------|------------|--------|----|--------|-----------|----------|-------------|---------------|----------|
| 1 | batch_orchestrator_v1 | qwen3.5_27b-temp0 [Qwen 3.5 27B (temperature 0)] | match-gatekeeper | qwen3.5_27b-temp0 [Qwen 3.5 27B (temperature 0)] | 3 | 3 | 0 | 0 | 0.333 | 0.222 | 0.850 | 0.828 | 0.986 | 1.000 | 1.000 |
