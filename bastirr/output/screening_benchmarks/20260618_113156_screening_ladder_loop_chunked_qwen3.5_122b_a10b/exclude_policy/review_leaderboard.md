# Review-Level Screening Benchmark Leaderboard

This file compares model configurations within each review.

Gold label policy: `exclude_label_0_5`

## stroke_theophylline_10

**Title:** Theophylline, aminophylline, caffeine and analogues for acute ischaemic stroke
**URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD000211.pub2/full
**Studies:** 10 | **Gold pass:** 2 | **Gold exclude:** 8

Metrics below are averaged only over scored runs with complete per-study decision coverage.

| Rank | Architecture | Gatekeeper Model | Orchestrator Policy | Orchestrator Model | Runs | Scored | Incomplete | Errors | F1 | Recall | Precision | Accuracy | Specificity | Parse Success | Coverage |
|------|--------------|------------------|---------------------|--------------------|------|--------|------------|--------|----|--------|-----------|----------|-------------|---------------|----------|
| 1 | loop_chunk_orchestrator_v1 | qwen3.5-122b-a10b [Qwen 3.5 122B A10B] | fixed | qwen3.5-122b-a10b [Qwen 3.5 122B A10B] | 1 | 1 | 0 | 0 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |

## alopecia_areata_25

**Title:** Interventions for alopecia areata
**URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD004413.pub2/full
**Studies:** 25 | **Gold pass:** 13 | **Gold exclude:** 12

Metrics below are averaged only over scored runs with complete per-study decision coverage.

| Rank | Architecture | Gatekeeper Model | Orchestrator Policy | Orchestrator Model | Runs | Scored | Incomplete | Errors | F1 | Recall | Precision | Accuracy | Specificity | Parse Success | Coverage |
|------|--------------|------------------|---------------------|--------------------|------|--------|------------|--------|----|--------|-----------|----------|-------------|---------------|----------|
| 1 | loop_chunk_orchestrator_v1 | qwen3.5-122b-a10b [Qwen 3.5 122B A10B] | fixed | qwen3.5-122b-a10b [Qwen 3.5 122B A10B] | 1 | 1 | 0 | 0 | 0.839 | 1.000 | 0.722 | 0.800 | 0.583 | 1.000 | 1.000 |

## iud_insertion_pain_50

**Title:** Interventions for pain with intrauterine device insertion
**URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD007373.pub3/full
**Studies:** 50 | **Gold pass:** 26 | **Gold exclude:** 24

Metrics below are averaged only over scored runs with complete per-study decision coverage.

| Rank | Architecture | Gatekeeper Model | Orchestrator Policy | Orchestrator Model | Runs | Scored | Incomplete | Errors | F1 | Recall | Precision | Accuracy | Specificity | Parse Success | Coverage |
|------|--------------|------------------|---------------------|--------------------|------|--------|------------|--------|----|--------|-----------|----------|-------------|---------------|----------|
| 1 | loop_chunk_orchestrator_v1 | qwen3.5-122b-a10b [Qwen 3.5 122B A10B] | fixed | qwen3.5-122b-a10b [Qwen 3.5 122B A10B] | 1 | 1 | 0 | 0 | 0.963 | 1.000 | 0.929 | 0.960 | 0.917 | 1.000 | 1.000 |

## pelvic_floor_training_100

**Title:** Pelvic floor muscle training versus no treatment, or inactive control treatments, for urinary incontinence in women
**URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD005654.pub4/full
**Studies:** 100 | **Gold pass:** 26 | **Gold exclude:** 74

Metrics below are averaged only over scored runs with complete per-study decision coverage.

| Rank | Architecture | Gatekeeper Model | Orchestrator Policy | Orchestrator Model | Runs | Scored | Incomplete | Errors | F1 | Recall | Precision | Accuracy | Specificity | Parse Success | Coverage |
|------|--------------|------------------|---------------------|--------------------|------|--------|------------|--------|----|--------|-----------|----------|-------------|---------------|----------|
| 1 | loop_chunk_orchestrator_v1 | qwen3.5-122b-a10b [Qwen 3.5 122B A10B] | fixed | qwen3.5-122b-a10b [Qwen 3.5 122B A10B] | 1 | 1 | 0 | 0 | 0.806 | 0.962 | 0.694 | 0.880 | 0.851 | 1.000 | 1.000 |

## heart_failure_mhealth_200

**Title:** mHealth education interventions in heart failure
**URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD011845.pub2/full
**Studies:** 200 | **Gold pass:** 4 | **Gold exclude:** 196

Metrics below are averaged only over scored runs with complete per-study decision coverage.

| Rank | Architecture | Gatekeeper Model | Orchestrator Policy | Orchestrator Model | Runs | Scored | Incomplete | Errors | F1 | Recall | Precision | Accuracy | Specificity | Parse Success | Coverage |
|------|--------------|------------------|---------------------|--------------------|------|--------|------------|--------|----|--------|-----------|----------|-------------|---------------|----------|
| 1 | loop_chunk_orchestrator_v1 | qwen3.5-122b-a10b [Qwen 3.5 122B A10B] | fixed | qwen3.5-122b-a10b [Qwen 3.5 122B A10B] | 1 | 1 | 0 | 0 | 0.136 | 1.000 | 0.073 | 0.745 | 0.740 | 1.000 | 1.000 |
