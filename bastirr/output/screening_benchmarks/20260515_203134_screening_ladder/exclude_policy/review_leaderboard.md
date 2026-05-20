# Review-Level Screening Benchmark Leaderboard

This file compares model configurations within each review.

Gold label policy: `exclude_label_0_5`

## stroke_theophylline_10

**Title:** Theophylline, aminophylline, caffeine and analogues for acute ischaemic stroke
**URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD000211.pub2/full
**Studies:** 10 | **Gold pass:** 2 | **Gold exclude:** 8

Metrics below are averaged only over scored runs with complete per-study decision coverage.

| Rank | Gatekeeper Model | Orchestrator Policy | Orchestrator Model | Runs | Scored | Incomplete | Errors | F1 | Recall | Precision | Accuracy | Specificity | Parse Success | Coverage |
|------|------------------|---------------------|--------------------|------|--------|------------|--------|----|--------|-----------|----------|-------------|---------------|----------|
| 1 | gpt-oss-120b [OpenAI GPT-OSS 120B] | fixed | gpt-oss-120b [OpenAI GPT-OSS 120B] | 1 | 1 | 0 | 0 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |

## alopecia_areata_25

**Title:** Interventions for alopecia areata
**URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD004413.pub2/full
**Studies:** 25 | **Gold pass:** 13 | **Gold exclude:** 12

Metrics below are averaged only over scored runs with complete per-study decision coverage.

| Rank | Gatekeeper Model | Orchestrator Policy | Orchestrator Model | Runs | Scored | Incomplete | Errors | F1 | Recall | Precision | Accuracy | Specificity | Parse Success | Coverage |
|------|------------------|---------------------|--------------------|------|--------|------------|--------|----|--------|-----------|----------|-------------|---------------|----------|
| 1 | gpt-oss-120b [OpenAI GPT-OSS 120B] | fixed | gpt-oss-120b [OpenAI GPT-OSS 120B] | 1 | 1 | 0 | 0 | 0.828 | 0.923 | 0.750 | 0.800 | 0.667 | 1.000 | 1.000 |

## iud_insertion_pain_50

**Title:** Interventions for pain with intrauterine device insertion
**URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD007373.pub3/full
**Studies:** 50 | **Gold pass:** 26 | **Gold exclude:** 24

Metrics below are averaged only over scored runs with complete per-study decision coverage.

| Rank | Gatekeeper Model | Orchestrator Policy | Orchestrator Model | Runs | Scored | Incomplete | Errors | F1 | Recall | Precision | Accuracy | Specificity | Parse Success | Coverage |
|------|------------------|---------------------|--------------------|------|--------|------------|--------|----|--------|-----------|----------|-------------|---------------|----------|
| 1 | gpt-oss-120b [OpenAI GPT-OSS 120B] | fixed | gpt-oss-120b [OpenAI GPT-OSS 120B] | 1 | 1 | 0 | 0 | 0.917 | 0.846 | 1.000 | 0.920 | 1.000 | 1.000 | 1.000 |

## pelvic_floor_training_100

**Title:** Pelvic floor muscle training versus no treatment, or inactive control treatments, for urinary incontinence in women
**URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD005654.pub4/full
**Studies:** 100 | **Gold pass:** 26 | **Gold exclude:** 74

Metrics below are averaged only over scored runs with complete per-study decision coverage.

| Rank | Gatekeeper Model | Orchestrator Policy | Orchestrator Model | Runs | Scored | Incomplete | Errors | F1 | Recall | Precision | Accuracy | Specificity | Parse Success | Coverage |
|------|------------------|---------------------|--------------------|------|--------|------------|--------|----|--------|-----------|----------|-------------|---------------|----------|
| 1 | gpt-oss-120b [OpenAI GPT-OSS 120B] | fixed | gpt-oss-120b [OpenAI GPT-OSS 120B] | 1 | 1 | 0 | 0 | 0.735 | 0.692 | 0.783 | 0.870 | 0.932 | 1.000 | 1.000 |

## heart_failure_mhealth_200

**Title:** mHealth education interventions in heart failure
**URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD011845.pub2/full
**Studies:** 200 | **Gold pass:** 4 | **Gold exclude:** 196

Metrics below are averaged only over scored runs with complete per-study decision coverage.

| Rank | Gatekeeper Model | Orchestrator Policy | Orchestrator Model | Runs | Scored | Incomplete | Errors | F1 | Recall | Precision | Accuracy | Specificity | Parse Success | Coverage |
|------|------------------|---------------------|--------------------|------|--------|------------|--------|----|--------|-----------|----------|-------------|---------------|----------|
| 1 | gpt-oss-120b [OpenAI GPT-OSS 120B] | fixed | gpt-oss-120b [OpenAI GPT-OSS 120B] | 1 | 1 | 0 | 0 | 0.222 | 0.250 | 0.200 | 0.965 | 0.980 | 1.000 | 1.000 |
