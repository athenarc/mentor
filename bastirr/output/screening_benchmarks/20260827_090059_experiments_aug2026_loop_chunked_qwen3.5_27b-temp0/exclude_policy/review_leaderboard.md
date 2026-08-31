# Review-Level Screening Benchmark Leaderboard

This file compares model configurations within each review.

Gold label policy: `exclude_label_0_5`

## 14651858_cd008040_pub3

**Title:** Paracetamol (acetaminophen) with or without an antiemetic for acute migraine headaches in adults
**URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD008040.pub3/full
**Studies:** 61 | **Gold pass:** 8 | **Gold exclude:** 53

Metrics below are averaged only over scored runs with complete per-study decision coverage.

| Rank | Architecture | Gatekeeper Model | Orchestrator Policy | Orchestrator Model | Runs | Scored | Incomplete | Errors | F1 | Recall | Precision | Accuracy | Specificity | Parse Success | Coverage |
|------|--------------|------------------|---------------------|--------------------|------|--------|------------|--------|----|--------|-----------|----------|-------------|---------------|----------|
| 1 | loop_chunk_orchestrator_v1 | qwen3.5_27b-temp0 [Qwen 3.5 27B (temperature 0)] | match-gatekeeper | qwen3.5_27b-temp0 [Qwen 3.5 27B (temperature 0)] | 3 | 3 | 0 | 0 | 0.842 | 1.000 | 0.727 | 0.951 | 0.943 | 1.000 | 1.000 |
