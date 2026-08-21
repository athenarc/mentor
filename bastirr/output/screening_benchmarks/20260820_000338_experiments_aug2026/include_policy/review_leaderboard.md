# Review-Level Screening Benchmark Leaderboard

This file compares model configurations within each review.

Gold label policy: `include_label_0_5`

## 14651858_cd007934_pub3

**Title:** De‐escalation of antimicrobial treatment for adults with sepsis, severe sepsis or septic shock
**URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD007934.pub3/full
**Studies:** 96 | **Gold pass:** 20 | **Gold exclude:** 76

Metrics below are averaged only over scored runs with complete per-study decision coverage.

| Rank | Architecture | Gatekeeper Model | Orchestrator Policy | Orchestrator Model | Runs | Scored | Incomplete | Errors | F1 | Recall | Precision | Accuracy | Specificity | Parse Success | Coverage |
|------|--------------|------------------|---------------------|--------------------|------|--------|------------|--------|----|--------|-----------|----------|-------------|---------------|----------|
| 1 | batch_orchestrator_v1 | qwen3.5_27b-temp0 [Qwen 3.5 27B (temperature 0)] | match-gatekeeper | qwen3.5_27b-temp0 [Qwen 3.5 27B (temperature 0)] | 3 | 3 | 0 | 0 | n/a | 0.000 | n/a | 0.792 | 1.000 | 1.000 | 1.000 |
