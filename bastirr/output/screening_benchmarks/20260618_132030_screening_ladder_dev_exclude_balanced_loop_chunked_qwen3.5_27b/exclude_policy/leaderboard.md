# Screening Benchmark Leaderboard

Gold label policy: `exclude_label_0_5`

Metrics are averaged only over scored runs with complete per-study decision coverage.

| Rank | Architecture | Gatekeeper Model | Orchestrator Policy | Orchestrator Model | Runs | Scored | Incomplete | Errors | F1 | Recall | Precision | Accuracy | Specificity | Parse Success | Coverage |
|------|--------------|------------------|---------------------|--------------------|------|--------|------------|--------|----|--------|-----------|----------|-------------|---------------|----------|
| 1 | loop_chunk_orchestrator_v1 | qwen3.5-27b [Qwen 3.5 27B] | fixed | qwen3.5-27b [Qwen 3.5 27B] | 5 | 5 | 0 | 0 | 0.926 | 0.959 | 0.897 | 0.922 | 0.882 | 1.000 | 1.000 |
