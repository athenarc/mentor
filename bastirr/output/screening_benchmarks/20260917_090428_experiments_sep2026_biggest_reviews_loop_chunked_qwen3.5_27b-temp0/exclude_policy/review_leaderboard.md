# Review-Level Screening Benchmark Leaderboard

This file compares model configurations within each review.

Gold label policy: `exclude_label_0_5`

## 14651858_cd012651

**Title:** Diet, physical activity and behavioural interventions for the treatment of overweight or obese children from the age of 6 to 11 years
**URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD012651/full
**Studies:** 456 | **Gold pass:** 65 | **Gold exclude:** 391

Metrics below are averaged only over scored runs with complete per-study decision coverage.

| Rank | Architecture | Gatekeeper Model | Orchestrator Policy | Orchestrator Model | Runs | Scored | Incomplete | Errors | F1 | Recall | Precision | Accuracy | Specificity | Parse Success | Coverage |
|------|--------------|------------------|---------------------|--------------------|------|--------|------------|--------|----|--------|-----------|----------|-------------|---------------|----------|
| 1 | loop_chunk_orchestrator_v1 | qwen3.5_27b-temp0 [Qwen 3.5 27B (temperature 0)] | match-gatekeeper | qwen3.5_27b-temp0 [Qwen 3.5 27B (temperature 0)] | 3 | 0 | 3 | 0 | n/a | n/a | n/a | n/a | n/a | 0.000 | 0.406 |
