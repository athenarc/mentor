# Review-Level Screening Benchmark Leaderboard

This file compares model configurations within each review.

Gold label policy: `exclude_label_0_5`

## 14651858_cd013274_pub2

**Title:** Consumers’ and health providers’ views and perceptions of partnering to improve health services design, delivery and evaluation: a co‐produced qualitative evidence synthesis
**URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD013274.pub2/full
**Studies:** 597 | **Gold pass:** 31 | **Gold exclude:** 566

Metrics below are averaged only over scored runs with complete per-study decision coverage.

| Rank | Architecture | Gatekeeper Model | Orchestrator Policy | Orchestrator Model | Runs | Scored | Incomplete | Errors | F1 | Recall | Precision | Accuracy | Specificity | Parse Success | Coverage |
|------|--------------|------------------|---------------------|--------------------|------|--------|------------|--------|----|--------|-----------|----------|-------------|---------------|----------|
| 1 | loop_chunk_orchestrator_v1 | qwen3.5_27b-temp0 [Qwen 3.5 27B (temperature 0)] | match-gatekeeper | qwen3.5_27b-temp0 [Qwen 3.5 27B (temperature 0)] | 3 | 2 | 1 | 0 | 0.144 | 0.887 | 0.079 | 0.454 | 0.430 | 0.667 | 0.834 |
