# Review-Level Screening Benchmark Leaderboard

This file compares model configurations within each review.

Gold label policy: `include_label_0_5`

## 14651858_cd013684

**Title:** Psychological interventions to foster resilience in healthcare students
**URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD013684/full
**Studies:** 446 | **Gold pass:** 34 | **Gold exclude:** 412

Metrics below are averaged only over scored runs with complete per-study decision coverage.

| Rank | Architecture | Gatekeeper Model | Orchestrator Policy | Orchestrator Model | Runs | Scored | Incomplete | Errors | F1 | Recall | Precision | Accuracy | Specificity | Parse Success | Coverage |
|------|--------------|------------------|---------------------|--------------------|------|--------|------------|--------|----|--------|-----------|----------|-------------|---------------|----------|
| 1 | loop_chunk_orchestrator_v1 | qwen3.5_27b-temp0 [Qwen 3.5 27B (temperature 0)] | match-gatekeeper | qwen3.5_27b-temp0 [Qwen 3.5 27B (temperature 0)] | 3 | 1 | 2 | 0 | 0.542 | 0.382 | 0.929 | 0.951 | 0.998 | 0.333 | 0.816 |
