# Review-Level Screening Benchmark Leaderboard

This file compares model configurations within each review.

Gold label policy: `include_label_0_5`

## 14651858_cd008500_pub5

**Title:** Primary prophylaxis for venous thromboembolism in ambulatory cancer patients receiving chemotherapy
**URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD008500.pub5/full
**Studies:** 83 | **Gold pass:** 46 | **Gold exclude:** 37

Metrics below are averaged only over scored runs with complete per-study decision coverage.

| Rank | Architecture | Gatekeeper Model | Orchestrator Policy | Orchestrator Model | Runs | Scored | Incomplete | Errors | F1 | Recall | Precision | Accuracy | Specificity | Parse Success | Coverage |
|------|--------------|------------------|---------------------|--------------------|------|--------|------------|--------|----|--------|-----------|----------|-------------|---------------|----------|
| 1 | loop_chunk_orchestrator_v1 | qwen3.5_27b-temp0 [Qwen 3.5 27B (temperature 0)] | match-gatekeeper | qwen3.5_27b-temp0 [Qwen 3.5 27B (temperature 0)] | 3 | 3 | 0 | 0 | 0.722 | 0.565 | 1.000 | 0.759 | 1.000 | 1.000 | 1.000 |
