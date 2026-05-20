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
| 1 | gpt-oss-120b [OpenAI GPT-OSS 120B] | fixed | gpt-oss-120b [OpenAI GPT-OSS 120B] | 1 | 1 | 0 | 0 | 0.750 | 0.600 | 1.000 | 0.800 | 1.000 | 1.000 | 1.000 |

## tricyclic_depression_children_25

**Title:** Tricyclic drugs for depression in children and adolescents
**URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD002317.pub2/full
**Studies:** 25 | **Gold pass:** 12 | **Gold exclude:** 13

Metrics below are averaged only over scored runs with complete per-study decision coverage.

| Rank | Gatekeeper Model | Orchestrator Policy | Orchestrator Model | Runs | Scored | Incomplete | Errors | F1 | Recall | Precision | Accuracy | Specificity | Parse Success | Coverage |
|------|------------------|---------------------|--------------------|------|--------|------------|--------|----|--------|-----------|----------|-------------|---------------|----------|
| 1 | gpt-oss-120b [OpenAI GPT-OSS 120B] | fixed | gpt-oss-120b [OpenAI GPT-OSS 120B] | 1 | 1 | 0 | 0 | 0.909 | 0.833 | 1.000 | 0.920 | 1.000 | 1.000 | 1.000 |

## adhesive_capsulitis_50

**Title:** Manual therapy and exercise for adhesive capsulitis (frozen shoulder)
**URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD011275/full
**Studies:** 50 | **Gold pass:** 25 | **Gold exclude:** 25

Metrics below are averaged only over scored runs with complete per-study decision coverage.

| Rank | Gatekeeper Model | Orchestrator Policy | Orchestrator Model | Runs | Scored | Incomplete | Errors | F1 | Recall | Precision | Accuracy | Specificity | Parse Success | Coverage |
|------|------------------|---------------------|--------------------|------|--------|------------|--------|----|--------|-----------|----------|-------------|---------------|----------|
| 1 | gpt-oss-120b [OpenAI GPT-OSS 120B] | fixed | gpt-oss-120b [OpenAI GPT-OSS 120B] | 1 | 1 | 0 | 0 | 0.863 | 0.880 | 0.846 | 0.860 | 0.840 | 1.000 | 1.000 |

## desmopressin_transfusion_100

**Title:** Desmopressin use for minimising perioperative blood transfusion
**URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD001884.pub3/full
**Studies:** 100 | **Gold pass:** 54 | **Gold exclude:** 46

Metrics below are averaged only over scored runs with complete per-study decision coverage.

| Rank | Gatekeeper Model | Orchestrator Policy | Orchestrator Model | Runs | Scored | Incomplete | Errors | F1 | Recall | Precision | Accuracy | Specificity | Parse Success | Coverage |
|------|------------------|---------------------|--------------------|------|--------|------------|--------|----|--------|-----------|----------|-------------|---------------|----------|
| 1 | gpt-oss-120b [OpenAI GPT-OSS 120B] | fixed | gpt-oss-120b [OpenAI GPT-OSS 120B] | 1 | 1 | 0 | 0 | 0.891 | 0.981 | 0.815 | 0.870 | 0.739 | 1.000 | 1.000 |

## prom_feedback_194

**Title:** Routine provision of feedback from patient‐reported outcome measurements to healthcare providers and patients in clinical practice
**URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD011589.pub2/full
**Studies:** 194 | **Gold pass:** 98 | **Gold exclude:** 96

Metrics below are averaged only over scored runs with complete per-study decision coverage.

| Rank | Gatekeeper Model | Orchestrator Policy | Orchestrator Model | Runs | Scored | Incomplete | Errors | F1 | Recall | Precision | Accuracy | Specificity | Parse Success | Coverage |
|------|------------------|---------------------|--------------------|------|--------|------------|--------|----|--------|-----------|----------|-------------|---------------|----------|
| 1 | gpt-oss-120b [OpenAI GPT-OSS 120B] | fixed | gpt-oss-120b [OpenAI GPT-OSS 120B] | 1 | 1 | 0 | 0 | 0.579 | 0.633 | 0.534 | 0.536 | 0.438 | 1.000 | 1.000 |
