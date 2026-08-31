# Review-Level Screening Benchmark Leaderboard

This file compares model configurations within each review.

Gold label policy: `include_label_0_5`

## 14651858_cd001865_pub3

**Title:** Personalised risk communication for informed decision making about taking screening tests
**URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD001865.pub3/full
**Studies:** 82 | **Gold pass:** 40 | **Gold exclude:** 42

Metrics below are averaged only over scored runs with complete per-study decision coverage.

| Rank | Architecture | Gatekeeper Model | Orchestrator Policy | Orchestrator Model | Runs | Scored | Incomplete | Errors | F1 | Recall | Precision | Accuracy | Specificity | Parse Success | Coverage |
|------|--------------|------------------|---------------------|--------------------|------|--------|------------|--------|----|--------|-----------|----------|-------------|---------------|----------|
| 1 | loop_chunk_orchestrator_v1 | qwen3.5_27b-temp0 [Qwen 3.5 27B (temperature 0)] | match-gatekeeper | qwen3.5_27b-temp0 [Qwen 3.5 27B (temperature 0)] | 3 | 2 | 1 | 0 | 0.831 | 0.713 | 1.000 | 0.860 | 1.000 | 0.667 | 0.829 |
