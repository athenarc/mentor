# Review-Level Screening Benchmark Leaderboard

This file compares model configurations within each review.

Gold label policy: `include_label_0_5`

## 14651858_cd006275_pub4

**Title:** Non‐pharmacological management of infant and young child procedural pain
**URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD006275.pub4/full
**Studies:** 424 | **Gold pass:** 378 | **Gold exclude:** 46

Metrics below are averaged only over scored runs with complete per-study decision coverage.

| Rank | Architecture | Gatekeeper Model | Orchestrator Policy | Orchestrator Model | Runs | Scored | Incomplete | Errors | F1 | Recall | Precision | Accuracy | Specificity | Parse Success | Coverage |
|------|--------------|------------------|---------------------|--------------------|------|--------|------------|--------|----|--------|-----------|----------|-------------|---------------|----------|
| 1 | loop_chunk_orchestrator_v1 | qwen3.5_27b-temp0 [Qwen 3.5 27B (temperature 0)] | match-gatekeeper | qwen3.5_27b-temp0 [Qwen 3.5 27B (temperature 0)] | 3 | 1 | 1 | 1 | 0.398 | 0.249 | 1.000 | 0.330 | 1.000 | 0.333 | 0.491 |
