# Review-Level Screening Benchmark Leaderboard

This file compares model configurations within each review.

Gold label policy: `exclude_label_0_5`

## 14651858_cd001911_pub4

**Title:** Carbamazepine versus phenytoin monotherapy for epilepsy: an individual participant data review
**URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD001911.pub4/full
**Studies:** 57 | **Gold pass:** 8 | **Gold exclude:** 49

Metrics below are averaged only over scored runs with complete per-study decision coverage.

| Rank | Architecture | Gatekeeper Model | Orchestrator Policy | Orchestrator Model | Runs | Scored | Incomplete | Errors | F1 | Recall | Precision | Accuracy | Specificity | Parse Success | Coverage |
|------|--------------|------------------|---------------------|--------------------|------|--------|------------|--------|----|--------|-----------|----------|-------------|---------------|----------|
| 1 | batch_orchestrator_v1 | qwen3.5_27b-temp0 [Qwen 3.5 27B (temperature 0)] | match-gatekeeper | qwen3.5_27b-temp0 [Qwen 3.5 27B (temperature 0)] | 3 | 3 | 0 | 0 | 0.646 | 0.875 | 0.513 | 0.865 | 0.864 | 1.000 | 1.000 |
