# Review-Level Screening Benchmark Leaderboard

This file compares model configurations within each review.

Gold label policy: `exclude_label_0_5`

## 14651858_cd001055_pub5

**Title:** Psychosocial interventions for supporting women to stop smoking in pregnancy
**URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD001055.pub5/full
**Studies:** 483 | **Gold pass:** 90 | **Gold exclude:** 393

Metrics below are averaged only over scored runs with complete per-study decision coverage.

| Rank | Architecture | Gatekeeper Model | Orchestrator Policy | Orchestrator Model | Runs | Scored | Incomplete | Errors | F1 | Recall | Precision | Accuracy | Specificity | Parse Success | Coverage |
|------|--------------|------------------|---------------------|--------------------|------|--------|------------|--------|----|--------|-----------|----------|-------------|---------------|----------|
| 1 | loop_chunk_orchestrator_v1 | qwen3.5_27b-temp0 [Qwen 3.5 27B (temperature 0)] | match-gatekeeper | qwen3.5_27b-temp0 [Qwen 3.5 27B (temperature 0)] | 3 | 3 | 0 | 0 | 0.785 | 0.800 | 0.773 | 0.918 | 0.945 | 1.000 | 1.000 |
