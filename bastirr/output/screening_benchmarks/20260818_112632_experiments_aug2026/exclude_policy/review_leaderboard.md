# Review-Level Screening Benchmark Leaderboard

This file compares model configurations within each review.

Gold label policy: `exclude_label_0_5`

## 14651858_cd007421_pub4

**Title:** Hyaluronic acid in embryo transfer media for assisted reproductive technologies
**URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD007421.pub4/full
**Studies:** 37 | **Gold pass:** 7 | **Gold exclude:** 30

Metrics below are averaged only over scored runs with complete per-study decision coverage.

| Rank | Architecture | Gatekeeper Model | Orchestrator Policy | Orchestrator Model | Runs | Scored | Incomplete | Errors | F1 | Recall | Precision | Accuracy | Specificity | Parse Success | Coverage |
|------|--------------|------------------|---------------------|--------------------|------|--------|------------|--------|----|--------|-----------|----------|-------------|---------------|----------|
| 1 | batch_orchestrator_v1 | qwen3.5_27b-temp0 [Qwen 3.5 27B (temperature 0)] | match-gatekeeper | qwen3.5_27b-temp0 [Qwen 3.5 27B (temperature 0)] | 3 | 3 | 0 | 0 | 0.669 | 0.714 | 0.632 | 0.865 | 0.900 | 1.000 | 1.000 |
