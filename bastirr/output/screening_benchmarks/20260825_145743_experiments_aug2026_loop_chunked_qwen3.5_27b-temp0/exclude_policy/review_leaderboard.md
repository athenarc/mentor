# Review-Level Screening Benchmark Leaderboard

This file compares model configurations within each review.

Gold label policy: `exclude_label_0_5`

## 14651858_cd004269_pub3

**Title:** Prophylactic platelet transfusion for prevention of bleeding in patients with haematological disorders after chemotherapy and stem cell transplantation
**URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD004269.pub3/full
**Studies:** 105 | **Gold pass:** 9 | **Gold exclude:** 96

Metrics below are averaged only over scored runs with complete per-study decision coverage.

| Rank | Architecture | Gatekeeper Model | Orchestrator Policy | Orchestrator Model | Runs | Scored | Incomplete | Errors | F1 | Recall | Precision | Accuracy | Specificity | Parse Success | Coverage |
|------|--------------|------------------|---------------------|--------------------|------|--------|------------|--------|----|--------|-----------|----------|-------------|---------------|----------|
| 1 | loop_chunk_orchestrator_v1 | qwen3.5_27b-temp0 [Qwen 3.5 27B (temperature 0)] | match-gatekeeper | qwen3.5_27b-temp0 [Qwen 3.5 27B (temperature 0)] | 3 | 3 | 0 | 0 | 0.397 | 0.963 | 0.250 | 0.749 | 0.729 | 1.000 | 1.000 |
