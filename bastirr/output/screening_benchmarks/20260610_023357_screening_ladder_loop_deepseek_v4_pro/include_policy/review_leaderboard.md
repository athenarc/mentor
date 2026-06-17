# Review-Level Screening Benchmark Leaderboard

This file compares model configurations within each review.

Gold label policy: `include_label_0_5`

## stroke_theophylline_10

**Title:** Theophylline, aminophylline, caffeine and analogues for acute ischaemic stroke
**URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD000211.pub2/full
**Studies:** 10 | **Gold pass:** 6 | **Gold exclude:** 4

Metrics below are averaged only over scored runs with complete per-study decision coverage.

| Rank | Architecture | Gatekeeper Model | Orchestrator Policy | Orchestrator Model | Runs | Scored | Incomplete | Errors | F1 | Recall | Precision | Accuracy | Specificity | Parse Success | Coverage |
|------|--------------|------------------|---------------------|--------------------|------|--------|------------|--------|----|--------|-----------|----------|-------------|---------------|----------|
| 1 | loop_orchestrator_v1 | deepseek-v4-pro [DeepSeek V4 Pro] | fixed | deepseek-v4-pro [DeepSeek V4 Pro] | 1 | 1 | 0 | 0 | 0.800 | 0.667 | 1.000 | 0.800 | 1.000 | 1.000 | 1.000 |

## alopecia_areata_25

**Title:** Interventions for alopecia areata
**URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD004413.pub2/full
**Studies:** 25 | **Gold pass:** 17 | **Gold exclude:** 8

Metrics below are averaged only over scored runs with complete per-study decision coverage.

| Rank | Architecture | Gatekeeper Model | Orchestrator Policy | Orchestrator Model | Runs | Scored | Incomplete | Errors | F1 | Recall | Precision | Accuracy | Specificity | Parse Success | Coverage |
|------|--------------|------------------|---------------------|--------------------|------|--------|------------|--------|----|--------|-----------|----------|-------------|---------------|----------|
| 1 | loop_orchestrator_v1 | deepseek-v4-pro [DeepSeek V4 Pro] | fixed | deepseek-v4-pro [DeepSeek V4 Pro] | 1 | 1 | 0 | 0 | 0.909 | 0.882 | 0.938 | 0.880 | 0.875 | 1.000 | 1.000 |

## iud_insertion_pain_50

**Title:** Interventions for pain with intrauterine device insertion
**URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD007373.pub3/full
**Studies:** 50 | **Gold pass:** 30 | **Gold exclude:** 20

Metrics below are averaged only over scored runs with complete per-study decision coverage.

| Rank | Architecture | Gatekeeper Model | Orchestrator Policy | Orchestrator Model | Runs | Scored | Incomplete | Errors | F1 | Recall | Precision | Accuracy | Specificity | Parse Success | Coverage |
|------|--------------|------------------|---------------------|--------------------|------|--------|------------|--------|----|--------|-----------|----------|-------------|---------------|----------|
| 1 | loop_orchestrator_v1 | deepseek-v4-pro [DeepSeek V4 Pro] | fixed | deepseek-v4-pro [DeepSeek V4 Pro] | 1 | 1 | 0 | 0 | 0.596 | 0.467 | 0.824 | 0.620 | 0.850 | 1.000 | 1.000 |

## pelvic_floor_training_100

**Title:** Pelvic floor muscle training versus no treatment, or inactive control treatments, for urinary incontinence in women
**URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD005654.pub4/full
**Studies:** 100 | **Gold pass:** 48 | **Gold exclude:** 52

Metrics below are averaged only over scored runs with complete per-study decision coverage.

| Rank | Architecture | Gatekeeper Model | Orchestrator Policy | Orchestrator Model | Runs | Scored | Incomplete | Errors | F1 | Recall | Precision | Accuracy | Specificity | Parse Success | Coverage |
|------|--------------|------------------|---------------------|--------------------|------|--------|------------|--------|----|--------|-----------|----------|-------------|---------------|----------|
| 1 | loop_orchestrator_v1 | deepseek-v4-pro [DeepSeek V4 Pro] | fixed | deepseek-v4-pro [DeepSeek V4 Pro] | 1 | 1 | 0 | 0 | 0.720 | 0.562 | 1.000 | 0.790 | 1.000 | 1.000 | 1.000 |

## heart_failure_mhealth_200

**Title:** mHealth education interventions in heart failure
**URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD011845.pub2/full
**Studies:** 200 | **Gold pass:** 137 | **Gold exclude:** 63

Metrics below are averaged only over scored runs with complete per-study decision coverage.

| Rank | Architecture | Gatekeeper Model | Orchestrator Policy | Orchestrator Model | Runs | Scored | Incomplete | Errors | F1 | Recall | Precision | Accuracy | Specificity | Parse Success | Coverage |
|------|--------------|------------------|---------------------|--------------------|------|--------|------------|--------|----|--------|-----------|----------|-------------|---------------|----------|
| 1 | loop_orchestrator_v1 | deepseek-v4-pro [DeepSeek V4 Pro] | fixed | deepseek-v4-pro [DeepSeek V4 Pro] | 1 | 1 | 0 | 0 | 0.122 | 0.066 | 0.818 | 0.350 | 0.968 | 1.000 | 1.000 |
