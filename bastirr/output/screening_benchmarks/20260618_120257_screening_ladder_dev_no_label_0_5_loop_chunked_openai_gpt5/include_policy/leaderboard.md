# Screening Benchmark Leaderboard

Gold label policy: `include_label_0_5`

Metrics are averaged only over scored runs with complete per-study decision coverage.

| Rank | Architecture | Gatekeeper Model | Orchestrator Policy | Orchestrator Model | Runs | Scored | Incomplete | Errors | F1 | Recall | Precision | Accuracy | Specificity | Parse Success | Coverage |
|------|--------------|------------------|---------------------|--------------------|------|--------|------------|--------|----|--------|-----------|----------|-------------|---------------|----------|
| 1 | loop_chunk_orchestrator_v1 | openai-gpt-5 [OpenAI GPT5] | fixed | openai-gpt-5 [OpenAI GPT5] | 5 | 5 | 0 | 0 | 0.950 | 0.933 | 0.970 | 0.944 | 0.966 | 1.000 | 1.000 |
