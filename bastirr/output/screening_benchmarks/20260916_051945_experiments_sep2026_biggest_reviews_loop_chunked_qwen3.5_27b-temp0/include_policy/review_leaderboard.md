# Review-Level Screening Benchmark Leaderboard

This file compares model configurations within each review.

Gold label policy: `include_label_0_5`

## 14651858_cd012859_pub2

**Title:** Drugs for preventing postoperative nausea and vomiting in adults after general anaesthesia: a network meta‐analysis
**URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD012859.pub2/full
**Studies:** 951 | **Gold pass:** 887 | **Gold exclude:** 64

Metrics below are averaged only over scored runs with complete per-study decision coverage.

| Rank | Architecture | Gatekeeper Model | Orchestrator Policy | Orchestrator Model | Runs | Scored | Incomplete | Errors | F1 | Recall | Precision | Accuracy | Specificity | Parse Success | Coverage |
|------|--------------|------------------|---------------------|--------------------|------|--------|------------|--------|----|--------|-----------|----------|-------------|---------------|----------|
| 1 | loop_chunk_orchestrator_v1 | qwen3.5_27b-temp0 [Qwen 3.5 27B (temperature 0)] | match-gatekeeper | qwen3.5_27b-temp0 [Qwen 3.5 27B (temperature 0)] | 3 | 3 | 0 | 0 | 0.839 | 0.723 | 0.999 | 0.741 | 0.995 | 1.000 | 1.000 |
