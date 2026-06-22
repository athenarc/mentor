# Screening Benchmark Leaderboard

Gold label policy: `include_label_0_5`

Metrics are averaged only over scored runs with complete per-study decision coverage.

| Rank | Architecture | Gatekeeper Model | Orchestrator Policy | Orchestrator Model | Runs | Scored | Incomplete | Errors | F1 | Recall | Precision | Accuracy | Specificity | Parse Success | Coverage |
|------|--------------|------------------|---------------------|--------------------|------|--------|------------|--------|----|--------|-----------|----------|-------------|---------------|----------|
| 1 | loop_chunk_orchestrator_v1 | nvidia-nemotron-3-super-120b-a12b [NVIDIA Nemotron 3 Super 120B A12B] | fixed | nvidia-nemotron-3-super-120b-a12b [NVIDIA Nemotron 3 Super 120B A12B] | 5 | 5 | 0 | 0 | 0.865 | 0.805 | 0.939 | 0.857 | 0.922 | 1.000 | 1.000 |
