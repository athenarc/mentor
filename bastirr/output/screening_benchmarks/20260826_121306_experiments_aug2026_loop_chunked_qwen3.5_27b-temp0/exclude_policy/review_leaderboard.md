# Review-Level Screening Benchmark Leaderboard

This file compares model configurations within each review.

Gold label policy: `exclude_label_0_5`

## 14651858_cd004424_pub2

**Title:** Antiepileptic drugs for preventing seizures in people with brain tumors
**URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD004424.pub2/full
**Studies:** 33 | **Gold pass:** 5 | **Gold exclude:** 28

Metrics below are averaged only over scored runs with complete per-study decision coverage.

| Rank | Architecture | Gatekeeper Model | Orchestrator Policy | Orchestrator Model | Runs | Scored | Incomplete | Errors | F1 | Recall | Precision | Accuracy | Specificity | Parse Success | Coverage |
|------|--------------|------------------|---------------------|--------------------|------|--------|------------|--------|----|--------|-----------|----------|-------------|---------------|----------|
| 1 | loop_chunk_orchestrator_v1 | qwen3.5_27b-temp0 [Qwen 3.5 27B (temperature 0)] | match-gatekeeper | qwen3.5_27b-temp0 [Qwen 3.5 27B (temperature 0)] | 3 | 2 | 0 | 1 | 0.586 | 0.700 | 0.522 | 0.848 | 0.875 | 0.667 | 0.667 |
