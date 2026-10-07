# Review-Level Screening Benchmark Leaderboard

This file compares model configurations within each review.

Gold label policy: `include_label_0_5`

## 14651858_cd011535_pub6

**Title:** Systemic pharmacological treatments for chronic plaque psoriasis: a network meta‐analysis
**URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD011535.pub6/full
**Studies:** 440 | **Gold pass:** 339 | **Gold exclude:** 101

Metrics below are averaged only over scored runs with complete per-study decision coverage.

| Rank | Architecture | Gatekeeper Model | Orchestrator Policy | Orchestrator Model | Runs | Scored | Incomplete | Errors | F1 | Recall | Precision | Accuracy | Specificity | Parse Success | Coverage |
|------|--------------|------------------|---------------------|--------------------|------|--------|------------|--------|----|--------|-----------|----------|-------------|---------------|----------|
| 1 | loop_chunk_orchestrator_v1 | qwen3.5_27b-temp0 [Qwen 3.5 27B (temperature 0)] | match-gatekeeper | qwen3.5_27b-temp0 [Qwen 3.5 27B (temperature 0)] | 3 | 2 | 1 | 0 | 0.826 | 0.709 | 0.990 | 0.770 | 0.975 | 0.667 | 0.818 |
