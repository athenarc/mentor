# Review-Level Screening Benchmark Leaderboard

This file compares model configurations within each review.

Gold label policy: `exclude_label_0_5`

## 14651858_cd015031_pub2

**Title:** Pars plana vitrectomy with internal limiting membrane flap versus pars plana vitrectomy with conventional internal limiting membrane peeling for large macular hole
**URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD015031.pub2/full
**Studies:** 50 | **Gold pass:** 3 | **Gold exclude:** 47

Metrics below are averaged only over scored runs with complete per-study decision coverage.

| Rank | Architecture | Gatekeeper Model | Orchestrator Policy | Orchestrator Model | Runs | Scored | Incomplete | Errors | F1 | Recall | Precision | Accuracy | Specificity | Parse Success | Coverage |
|------|--------------|------------------|---------------------|--------------------|------|--------|------------|--------|----|--------|-----------|----------|-------------|---------------|----------|
| 1 | batch_orchestrator_v1 | qwen3.5_27b-temp0 [Qwen 3.5 27B (temperature 0)] | match-gatekeeper | qwen3.5_27b-temp0 [Qwen 3.5 27B (temperature 0)] | 3 | 3 | 0 | 0 | 0.730 | 0.778 | 0.694 | 0.967 | 0.979 | 1.000 | 1.000 |
