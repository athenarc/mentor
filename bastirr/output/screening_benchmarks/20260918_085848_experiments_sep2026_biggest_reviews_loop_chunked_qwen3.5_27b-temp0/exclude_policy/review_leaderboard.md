# Review-Level Screening Benchmark Leaderboard

This file compares model configurations within each review.

Gold label policy: `exclude_label_0_5`

## 14651858_cd009885_pub3

**Title:** Methylphenidate for children and adolescents with attention deficit hyperactivity disorder (ADHD)
**URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD009885.pub3/full
**Studies:** 509 | **Gold pass:** 206 | **Gold exclude:** 303

Metrics below are averaged only over scored runs with complete per-study decision coverage.

| Rank | Architecture | Gatekeeper Model | Orchestrator Policy | Orchestrator Model | Runs | Scored | Incomplete | Errors | F1 | Recall | Precision | Accuracy | Specificity | Parse Success | Coverage |
|------|--------------|------------------|---------------------|--------------------|------|--------|------------|--------|----|--------|-----------|----------|-------------|---------------|----------|
| 1 | loop_chunk_orchestrator_v1 | qwen3.5_27b-temp0 [Qwen 3.5 27B (temperature 0)] | match-gatekeeper | qwen3.5_27b-temp0 [Qwen 3.5 27B (temperature 0)] | 3 | 2 | 1 | 0 | 0.716 | 0.801 | 0.648 | 0.743 | 0.703 | 0.667 | 0.732 |
