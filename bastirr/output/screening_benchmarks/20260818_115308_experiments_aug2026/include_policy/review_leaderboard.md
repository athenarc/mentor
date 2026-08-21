# Review-Level Screening Benchmark Leaderboard

This file compares model configurations within each review.

Gold label policy: `include_label_0_5`

## 14651858_cd007362_pub2

**Title:** Sugammadex, a selective reversal medication for preventing postoperative residual neuromuscular blockade
**URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD007362.pub2/full
**Studies:** 39 | **Gold pass:** 11 | **Gold exclude:** 28

Metrics below are averaged only over scored runs with complete per-study decision coverage.

| Rank | Architecture | Gatekeeper Model | Orchestrator Policy | Orchestrator Model | Runs | Scored | Incomplete | Errors | F1 | Recall | Precision | Accuracy | Specificity | Parse Success | Coverage |
|------|--------------|------------------|---------------------|--------------------|------|--------|------------|--------|----|--------|-----------|----------|-------------|---------------|----------|
| 1 | batch_orchestrator_v1 | qwen3.5_27b-temp0 [Qwen 3.5 27B (temperature 0)] | match-gatekeeper | qwen3.5_27b-temp0 [Qwen 3.5 27B (temperature 0)] | 3 | 3 | 0 | 0 | 0.916 | 0.848 | 1.000 | 0.957 | 1.000 | 1.000 | 1.000 |
