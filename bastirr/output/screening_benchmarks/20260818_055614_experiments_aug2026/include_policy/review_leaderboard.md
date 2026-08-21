# Review-Level Screening Benchmark Leaderboard

This file compares model configurations within each review.

Gold label policy: `include_label_0_5`

## 14651858_cd006269_pub2

**Title:** Concomitant hyperthermia and radiation therapy for treating locally advanced rectal cancer
**URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD006269.pub2/full
**Studies:** 46 | **Gold pass:** 20 | **Gold exclude:** 26

Metrics below are averaged only over scored runs with complete per-study decision coverage.

| Rank | Architecture | Gatekeeper Model | Orchestrator Policy | Orchestrator Model | Runs | Scored | Incomplete | Errors | F1 | Recall | Precision | Accuracy | Specificity | Parse Success | Coverage |
|------|--------------|------------------|---------------------|--------------------|------|--------|------------|--------|----|--------|-----------|----------|-------------|---------------|----------|
| 1 | batch_orchestrator_v1 | qwen3.5_27b-temp0 [Qwen 3.5 27B (temperature 0)] | match-gatekeeper | qwen3.5_27b-temp0 [Qwen 3.5 27B (temperature 0)] | 3 | 3 | 0 | 0 | 0.369 | 0.283 | 0.621 | 0.572 | 0.795 | 1.000 | 1.000 |
