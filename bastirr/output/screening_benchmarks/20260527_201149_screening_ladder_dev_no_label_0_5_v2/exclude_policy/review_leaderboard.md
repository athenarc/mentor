# Review-Level Screening Benchmark Leaderboard

This file compares model configurations within each review.

Gold label policy: `exclude_label_0_5`

## endometrial_progestagens_10

**Title:** Adjuvant progestagens for endometrial cancer
**URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD001040.pub2/full
**Studies:** 10 | **Gold pass:** 5 | **Gold exclude:** 5

Metrics below are averaged only over scored runs with complete per-study decision coverage.

| Rank | Gatekeeper Model | Orchestrator Policy | Orchestrator Model | Runs | Scored | Incomplete | Errors | F1 | Recall | Precision | Accuracy | Specificity | Parse Success | Coverage |
|------|------------------|---------------------|--------------------|------|--------|------------|--------|----|--------|-----------|----------|-------------|---------------|----------|
| 1 | openai-gpt-5--xhigh [OpenAI GPT5] | fixed | openai-gpt-5--xhigh [OpenAI GPT5] | 1 | 1 | 0 | 0 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |

## glucocorticoids_rheumatoid_26

**Title:** Effects of glucocorticoids on radiological progression in rheumatoid arthritis
**URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD006356/full
**Studies:** 26 | **Gold pass:** 12 | **Gold exclude:** 14

Metrics below are averaged only over scored runs with complete per-study decision coverage.

| Rank | Gatekeeper Model | Orchestrator Policy | Orchestrator Model | Runs | Scored | Incomplete | Errors | F1 | Recall | Precision | Accuracy | Specificity | Parse Success | Coverage |
|------|------------------|---------------------|--------------------|------|--------|------------|--------|----|--------|-----------|----------|-------------|---------------|----------|
| 1 | openai-gpt-5--xhigh [OpenAI GPT5] | fixed | openai-gpt-5--xhigh [OpenAI GPT5] | 1 | 1 | 0 | 0 | 0.889 | 1.000 | 0.800 | 0.885 | 0.786 | 1.000 | 1.000 |

## vitamin_d_ckd_not_dialysis_51

**Title:** Vitamin D compounds for people with chronic kidney disease not requiring dialysis
**URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD008175/full
**Studies:** 51 | **Gold pass:** 14 | **Gold exclude:** 37

Metrics below are averaged only over scored runs with complete per-study decision coverage.

| Rank | Gatekeeper Model | Orchestrator Policy | Orchestrator Model | Runs | Scored | Incomplete | Errors | F1 | Recall | Precision | Accuracy | Specificity | Parse Success | Coverage |
|------|------------------|---------------------|--------------------|------|--------|------------|--------|----|--------|-----------|----------|-------------|---------------|----------|
| 1 | openai-gpt-5--xhigh [OpenAI GPT5] | fixed | openai-gpt-5--xhigh [OpenAI GPT5] | 1 | 1 | 0 | 0 | 0.353 | 0.214 | 1.000 | 0.784 | 1.000 | 1.000 | 1.000 |

## continuity_of_care_cancer_92

**Title:** Interventions to improve continuity of care in the follow‐up of patients with cancer
**URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD007672.pub2/full
**Studies:** 92 | **Gold pass:** 42 | **Gold exclude:** 50

Metrics below are averaged only over scored runs with complete per-study decision coverage.

| Rank | Gatekeeper Model | Orchestrator Policy | Orchestrator Model | Runs | Scored | Incomplete | Errors | F1 | Recall | Precision | Accuracy | Specificity | Parse Success | Coverage |
|------|------------------|---------------------|--------------------|------|--------|------------|--------|----|--------|-----------|----------|-------------|---------------|----------|
| 1 | openai-gpt-5--xhigh [OpenAI GPT5] | fixed | openai-gpt-5--xhigh [OpenAI GPT5] | 1 | 1 | 0 | 0 | 0.778 | 0.667 | 0.933 | 0.826 | 0.960 | 1.000 | 1.000 |

## glaucoma_140

**Title:** Optic nerve head and fibre layer imaging for diagnosing glaucoma
**URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD008803.pub2/full
**Studies:** 140 | **Gold pass:** 96 | **Gold exclude:** 44

Metrics below are averaged only over scored runs with complete per-study decision coverage.

| Rank | Gatekeeper Model | Orchestrator Policy | Orchestrator Model | Runs | Scored | Incomplete | Errors | F1 | Recall | Precision | Accuracy | Specificity | Parse Success | Coverage |
|------|------------------|---------------------|--------------------|------|--------|------------|--------|----|--------|-----------|----------|-------------|---------------|----------|
| 1 | openai-gpt-5--xhigh [OpenAI GPT5] | fixed | openai-gpt-5--xhigh [OpenAI GPT5] | 1 | 1 | 0 | 0 | 0.990 | 1.000 | 0.980 | 0.986 | 0.955 | 1.000 | 1.000 |
