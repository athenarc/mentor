# Review-Level Screening Benchmark Leaderboard

This file compares model configurations within each review.

Gold label policy: `exclude_label_0_5`

## 14651858_cd001865_pub3

**Title:** Personalised risk communication for informed decision making about taking screening tests
**URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD001865.pub3/full
**Studies:** 82 | **Gold pass:** 27 | **Gold exclude:** 55

Metrics below are averaged only over scored runs with complete per-study decision coverage.

| Rank | Architecture | Gatekeeper Model | Orchestrator Policy | Orchestrator Model | Runs | Scored | Incomplete | Errors | F1 | Recall | Precision | Accuracy | Specificity | Parse Success | Coverage |
|------|--------------|------------------|---------------------|--------------------|------|--------|------------|--------|----|--------|-----------|----------|-------------|---------------|----------|
| 1 | loop_chunk_orchestrator_v1 | qwen3.5_27b-temp0 [Qwen 3.5 27B (temperature 0)] | match-gatekeeper | qwen3.5_27b-temp0 [Qwen 3.5 27B (temperature 0)] | 3 | 2 | 1 | 0 | 0.846 | 0.870 | 0.826 | 0.896 | 0.909 | 0.667 | 0.829 |
