# Review-Level Screening Benchmark Leaderboard

This file compares model configurations within each review.

Gold label policy: `include_label_0_5`

## 14651858_cd008605_pub4

**Title:** Dopamine agonists for preventing ovarian hyperstimulation syndrome
**URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD008605.pub4/full
**Studies:** 66 | **Gold pass:** 26 | **Gold exclude:** 40

Metrics below are averaged only over scored runs with complete per-study decision coverage.

| Rank | Architecture | Gatekeeper Model | Orchestrator Policy | Orchestrator Model | Runs | Scored | Incomplete | Errors | F1 | Recall | Precision | Accuracy | Specificity | Parse Success | Coverage |
|------|--------------|------------------|---------------------|--------------------|------|--------|------------|--------|----|--------|-----------|----------|-------------|---------------|----------|
| 1 | batch_orchestrator_v1 | qwen3.5_27b-temp0 [Qwen 3.5 27B (temperature 0)] | match-gatekeeper | qwen3.5_27b-temp0 [Qwen 3.5 27B (temperature 0)] | 3 | 3 | 0 | 0 | 0.761 | 0.615 | 1.000 | 0.848 | 1.000 | 1.000 | 1.000 |
