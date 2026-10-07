# Review-Level Screening Benchmark Leaderboard

This file compares model configurations within each review.

Gold label policy: `include_label_0_5`

## 14651858_cd000011_pub4

**Title:** Interventions for enhancing medication adherence
**URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD000011.pub4/full
**Studies:** 518 | **Gold pass:** 503 | **Gold exclude:** 15

Metrics below are averaged only over scored runs with complete per-study decision coverage.

| Rank | Architecture | Gatekeeper Model | Orchestrator Policy | Orchestrator Model | Runs | Scored | Incomplete | Errors | F1 | Recall | Precision | Accuracy | Specificity | Parse Success | Coverage |
|------|--------------|------------------|---------------------|--------------------|------|--------|------------|--------|----|--------|-----------|----------|-------------|---------------|----------|
| 1 | loop_chunk_orchestrator_v1 | qwen3.5_27b-temp0 [Qwen 3.5 27B (temperature 0)] | match-gatekeeper | qwen3.5_27b-temp0 [Qwen 3.5 27B (temperature 0)] | 3 | 2 | 1 | 0 | 0.727 | 0.574 | 0.995 | 0.583 | 0.900 | 0.667 | 0.860 |
