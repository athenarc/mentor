# Review-Level Screening Benchmark Leaderboard

This file compares model configurations within each review.

Gold label policy: `exclude_label_0_5`

## 14651858_cd005460_pub3

**Title:** Traditional birth attendant training for improving health behaviours and pregnancy outcomes
**URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD005460.pub3/full
**Studies:** 33 | **Gold pass:** 4 | **Gold exclude:** 29

Metrics below are averaged only over scored runs with complete per-study decision coverage.

| Rank | Architecture | Gatekeeper Model | Orchestrator Policy | Orchestrator Model | Runs | Scored | Incomplete | Errors | F1 | Recall | Precision | Accuracy | Specificity | Parse Success | Coverage |
|------|--------------|------------------|---------------------|--------------------|------|--------|------------|--------|----|--------|-----------|----------|-------------|---------------|----------|
| 1 | batch_orchestrator_v1 | qwen3.5_27b-temp0 [Qwen 3.5 27B (temperature 0)] | match-gatekeeper | qwen3.5_27b-temp0 [Qwen 3.5 27B (temperature 0)] | 2 | 2 | 0 | 0 | 0.750 | 0.750 | 0.750 | 0.939 | 0.966 | 1.000 | 1.000 |

## 14651858_cd008500_pub5

**Title:** Primary prophylaxis for venous thromboembolism in ambulatory cancer patients receiving chemotherapy
**URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD008500.pub5/full
**Studies:** 83 | **Gold pass:** 31 | **Gold exclude:** 52

Metrics below are averaged only over scored runs with complete per-study decision coverage.

| Rank | Architecture | Gatekeeper Model | Orchestrator Policy | Orchestrator Model | Runs | Scored | Incomplete | Errors | F1 | Recall | Precision | Accuracy | Specificity | Parse Success | Coverage |
|------|--------------|------------------|---------------------|--------------------|------|--------|------------|--------|----|--------|-----------|----------|-------------|---------------|----------|
| 1 | batch_orchestrator_v1 | qwen3.5_27b-temp0 [Qwen 3.5 27B (temperature 0)] | match-gatekeeper | qwen3.5_27b-temp0 [Qwen 3.5 27B (temperature 0)] | 2 | 2 | 0 | 0 | 0.904 | 0.839 | 0.981 | 0.934 | 0.990 | 1.000 | 1.000 |
