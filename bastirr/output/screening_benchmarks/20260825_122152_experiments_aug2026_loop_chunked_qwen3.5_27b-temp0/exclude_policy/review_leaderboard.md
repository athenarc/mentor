# Review-Level Screening Benchmark Leaderboard

This file compares model configurations within each review.

Gold label policy: `exclude_label_0_5`

## 14651858_cd010436_pub2

**Title:** Steroid‐eluting sinus stents for improving symptoms in chronic rhinosinusitis patients undergoing functional endoscopic sinus surgery
**URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD010436.pub2/full
**Studies:** 37 | **Gold pass:** 0 | **Gold exclude:** 37

Metrics below are averaged only over scored runs with complete per-study decision coverage.

| Rank | Architecture | Gatekeeper Model | Orchestrator Policy | Orchestrator Model | Runs | Scored | Incomplete | Errors | F1 | Recall | Precision | Accuracy | Specificity | Parse Success | Coverage |
|------|--------------|------------------|---------------------|--------------------|------|--------|------------|--------|----|--------|-----------|----------|-------------|---------------|----------|
| 1 | loop_chunk_orchestrator_v1 | qwen3.5_27b-temp0 [Qwen 3.5 27B (temperature 0)] | match-gatekeeper | qwen3.5_27b-temp0 [Qwen 3.5 27B (temperature 0)] | 3 | 3 | 0 | 0 | n/a | n/a | 0.000 | 0.883 | 0.883 | 1.000 | 1.000 |
