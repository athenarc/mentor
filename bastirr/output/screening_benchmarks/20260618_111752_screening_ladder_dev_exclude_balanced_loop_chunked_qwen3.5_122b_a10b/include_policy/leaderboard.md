# Screening Benchmark Leaderboard

Gold label policy: `include_label_0_5`

Metrics are averaged only over scored runs with complete per-study decision coverage.

| Rank | Architecture | Gatekeeper Model | Orchestrator Policy | Orchestrator Model | Runs | Scored | Incomplete | Errors | F1 | Recall | Precision | Accuracy | Specificity | Parse Success | Coverage |
|------|--------------|------------------|---------------------|--------------------|------|--------|------------|--------|----|--------|-----------|----------|-------------|---------------|----------|
| 1 | loop_chunk_orchestrator_v1 | qwen3.5-122b-a10b [Qwen 3.5 122B A10B] | fixed | qwen3.5-122b-a10b [Qwen 3.5 122B A10B] | 5 | 5 | 0 | 0 | 0.915 | 0.853 | 0.993 | 0.896 | 0.983 | 1.000 | 1.000 |
