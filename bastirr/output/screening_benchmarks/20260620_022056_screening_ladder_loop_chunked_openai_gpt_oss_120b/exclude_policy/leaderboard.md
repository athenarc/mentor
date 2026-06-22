# Screening Benchmark Leaderboard

Gold label policy: `exclude_label_0_5`

Metrics are averaged only over scored runs with complete per-study decision coverage.

| Rank | Architecture | Gatekeeper Model | Orchestrator Policy | Orchestrator Model | Runs | Scored | Incomplete | Errors | F1 | Recall | Precision | Accuracy | Specificity | Parse Success | Coverage |
|------|--------------|------------------|---------------------|--------------------|------|--------|------------|--------|----|--------|-----------|----------|-------------|---------------|----------|
| 1 | loop_chunk_orchestrator_v1 | gpt-oss-120b [OpenAI GPT-OSS 120B] | fixed | gpt-oss-120b [OpenAI GPT-OSS 120B] | 5 | 5 | 0 | 0 | 0.790 | 0.938 | 0.722 | 0.903 | 0.864 | 1.000 | 1.000 |
