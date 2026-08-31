# Review-Level Screening Benchmark Leaderboard

This file compares model configurations within each review.

Gold label policy: `exclude_label_0_5`

## 14651858_cd009012_pub3

**Title:** Early versus delayed antiretroviral treatment in HIV‐positive people with cryptococcal meningitis
**URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD009012.pub3/full
**Studies:** 30 | **Gold pass:** 4 | **Gold exclude:** 26

Metrics below are averaged only over scored runs with complete per-study decision coverage.

| Rank | Architecture | Gatekeeper Model | Orchestrator Policy | Orchestrator Model | Runs | Scored | Incomplete | Errors | F1 | Recall | Precision | Accuracy | Specificity | Parse Success | Coverage |
|------|--------------|------------------|---------------------|--------------------|------|--------|------------|--------|----|--------|-----------|----------|-------------|---------------|----------|
| 1 | loop_chunk_orchestrator_v1 | qwen3.5_27b-temp0 [Qwen 3.5 27B (temperature 0)] | match-gatekeeper | qwen3.5_27b-temp0 [Qwen 3.5 27B (temperature 0)] | 1 | 1 | 0 | 0 | 0.857 | 0.750 | 1.000 | 0.967 | 1.000 | 1.000 | 1.000 |
