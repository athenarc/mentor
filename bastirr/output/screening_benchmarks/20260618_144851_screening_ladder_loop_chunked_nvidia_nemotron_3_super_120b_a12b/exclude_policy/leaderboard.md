# Screening Benchmark Leaderboard

Gold label policy: `exclude_label_0_5`

Metrics are averaged only over scored runs with complete per-study decision coverage.

| Rank | Architecture | Gatekeeper Model | Orchestrator Policy | Orchestrator Model | Runs | Scored | Incomplete | Errors | F1 | Recall | Precision | Accuracy | Specificity | Parse Success | Coverage |
|------|--------------|------------------|---------------------|--------------------|------|--------|------------|--------|----|--------|-----------|----------|-------------|---------------|----------|
| 1 | loop_chunk_orchestrator_v1 | nvidia-nemotron-3-super-120b-a12b [NVIDIA Nemotron 3 Super 120B A12B] | fixed | nvidia-nemotron-3-super-120b-a12b [NVIDIA Nemotron 3 Super 120B A12B] | 5 | 4 | 1 | 0 | 0.651 | 0.962 | 0.563 | 0.833 | 0.784 | 0.800 | 0.850 |
