# Review-Level Screening Benchmark Leaderboard

This file compares model configurations within each review.

Gold label policy: `include_label_0_5`

## 14651858_cd014873_pub2

**Title:** A meta‐ethnography of how children and young people with chronic non‐cancer pain and their families experience and understand their condition, pain services, and treatments
**URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD014873.pub2/full
**Studies:** 520 | **Gold pass:** 429 | **Gold exclude:** 91

Metrics below are averaged only over scored runs with complete per-study decision coverage.

| Rank | Architecture | Gatekeeper Model | Orchestrator Policy | Orchestrator Model | Runs | Scored | Incomplete | Errors | F1 | Recall | Precision | Accuracy | Specificity | Parse Success | Coverage |
|------|--------------|------------------|---------------------|--------------------|------|--------|------------|--------|----|--------|-----------|----------|-------------|---------------|----------|
| 1 | loop_chunk_orchestrator_v1 | qwen3.5_27b-temp0 [Qwen 3.5 27B (temperature 0)] | match-gatekeeper | qwen3.5_27b-temp0 [Qwen 3.5 27B (temperature 0)] | 3 | 2 | 1 | 0 | 0.777 | 0.645 | 0.981 | 0.696 | 0.940 | 0.667 | 0.987 |
