# Review-Level Screening Benchmark Leaderboard

This file compares model configurations within each review.

Gold label policy: `exclude_label_0_5`

## stroke_theophylline_10

**Title:** Theophylline, aminophylline, caffeine and analogues for acute ischaemic stroke
**URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD000211.pub2/full
**Studies:** 10 | **Gold pass:** 2 | **Gold exclude:** 8

| Rank | Gatekeeper Model | Orchestrator Policy | Orchestrator Model | Runs | F1 | Recall | Precision | Accuracy | Specificity | Parse Success | Coverage |
|------|------------------|---------------------|--------------------|------|----|--------|-----------|----------|-------------|---------------|----------|
| 1 | gpt-5 [OpenAI API] | fixed | gpt-5 [OpenAI API] | 5 | 0.867 | 1.000 | 0.800 | 0.920 | 0.900 | 1.000 | 1.000 |

## alopecia_areata_25

**Title:** Interventions for alopecia areata
**URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD004413.pub2/full
**Studies:** 25 | **Gold pass:** 13 | **Gold exclude:** 12

| Rank | Gatekeeper Model | Orchestrator Policy | Orchestrator Model | Runs | F1 | Recall | Precision | Accuracy | Specificity | Parse Success | Coverage |
|------|------------------|---------------------|--------------------|------|----|--------|-----------|----------|-------------|---------------|----------|
| 1 | gpt-5 [OpenAI API] | fixed | gpt-5 [OpenAI API] | 5 | 0.834 | 0.923 | 0.761 | 0.808 | 0.683 | 1.000 | 1.000 |

## iud_insertion_pain_50

**Title:** Interventions for pain with intrauterine device insertion
**URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD007373.pub3/full
**Studies:** 50 | **Gold pass:** 26 | **Gold exclude:** 24

| Rank | Gatekeeper Model | Orchestrator Policy | Orchestrator Model | Runs | F1 | Recall | Precision | Accuracy | Specificity | Parse Success | Coverage |
|------|------------------|---------------------|--------------------|------|----|--------|-----------|----------|-------------|---------------|----------|
| 1 | gpt-5 [OpenAI API] | fixed | gpt-5 [OpenAI API] | 5 | 0.961 | 0.962 | 0.962 | 0.960 | 0.958 | 1.000 | 1.000 |

## pelvic_floor_training_100

**Title:** Pelvic floor muscle training versus no treatment, or inactive control treatments, for urinary incontinence in women
**URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD005654.pub4/full
**Studies:** 100 | **Gold pass:** 26 | **Gold exclude:** 74

| Rank | Gatekeeper Model | Orchestrator Policy | Orchestrator Model | Runs | F1 | Recall | Precision | Accuracy | Specificity | Parse Success | Coverage |
|------|------------------|---------------------|--------------------|------|----|--------|-----------|----------|-------------|---------------|----------|
| 1 | gpt-5 [OpenAI API] | fixed | gpt-5 [OpenAI API] | 5 | 0.848 | 0.885 | 0.816 | 0.918 | 0.930 | 1.000 | 1.000 |

## heart_failure_mhealth_200

**Title:** mHealth education interventions in heart failure
**URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD011845.pub2/full
**Studies:** 200 | **Gold pass:** 4 | **Gold exclude:** 196

| Rank | Gatekeeper Model | Orchestrator Policy | Orchestrator Model | Runs | F1 | Recall | Precision | Accuracy | Specificity | Parse Success | Coverage |
|------|------------------|---------------------|--------------------|------|----|--------|-----------|----------|-------------|---------------|----------|
| 1 | gpt-5 [OpenAI API] | fixed | gpt-5 [OpenAI API] | 5 | 0.819 | 0.800 | 0.733 | 0.986 | 0.990 | 0.600 | 0.605 |
