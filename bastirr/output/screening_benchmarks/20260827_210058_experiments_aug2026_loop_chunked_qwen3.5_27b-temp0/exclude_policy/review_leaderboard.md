# Review-Level Screening Benchmark Leaderboard

This file compares model configurations within each review.

Gold label policy: `exclude_label_0_5`

## 14651858_cd004920_pub3

**Title:** Antifungal agents for preventing fungal infections in non‐neutropenic critically ill patients
**URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD004920.pub3/full
**Studies:** 70 | **Gold pass:** 17 | **Gold exclude:** 53

Metrics below are averaged only over scored runs with complete per-study decision coverage.

| Rank | Architecture | Gatekeeper Model | Orchestrator Policy | Orchestrator Model | Runs | Scored | Incomplete | Errors | F1 | Recall | Precision | Accuracy | Specificity | Parse Success | Coverage |
|------|--------------|------------------|---------------------|--------------------|------|--------|------------|--------|----|--------|-----------|----------|-------------|---------------|----------|
| 1 | loop_chunk_orchestrator_v1 | qwen3.5_27b-temp0 [Qwen 3.5 27B (temperature 0)] | match-gatekeeper | qwen3.5_27b-temp0 [Qwen 3.5 27B (temperature 0)] | 3 | 2 | 0 | 1 | 0.784 | 0.853 | 0.726 | 0.886 | 0.896 | 0.667 | 0.667 |
