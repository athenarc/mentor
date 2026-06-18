# Review-Level Screening Benchmark Leaderboard

This file compares model configurations within each review.

Gold label policy: `include_label_0_5`

## surgical_termination_10

**Title:** Surgical methods for first trimester termination of pregnancy
**URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD002900/full
**Studies:** 10 | **Gold pass:** 7 | **Gold exclude:** 3

Metrics below are averaged only over scored runs with complete per-study decision coverage.

| Rank | Architecture | Gatekeeper Model | Orchestrator Policy | Orchestrator Model | Runs | Scored | Incomplete | Errors | F1 | Recall | Precision | Accuracy | Specificity | Parse Success | Coverage |
|------|--------------|------------------|---------------------|--------------------|------|--------|------------|--------|----|--------|-----------|----------|-------------|---------------|----------|
| 1 | loop_chunk_orchestrator_v1 | kimi-k2.6 [Kimi K2.6] | fixed | kimi-k2.6 [Kimi K2.6] | 1 | 1 | 0 | 0 | 0.833 | 0.714 | 1.000 | 0.800 | 1.000 | 1.000 | 1.000 |

## advanced_endometrial_carcinoma_24

**Title:** Chemotherapy for advanced, recurrent or metastatic endometrial carcinoma
**URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD003915.pub4/full
**Studies:** 24 | **Gold pass:** 12 | **Gold exclude:** 12

Metrics below are averaged only over scored runs with complete per-study decision coverage.

| Rank | Architecture | Gatekeeper Model | Orchestrator Policy | Orchestrator Model | Runs | Scored | Incomplete | Errors | F1 | Recall | Precision | Accuracy | Specificity | Parse Success | Coverage |
|------|--------------|------------------|---------------------|--------------------|------|--------|------------|--------|----|--------|-----------|----------|-------------|---------------|----------|
| 1 | loop_chunk_orchestrator_v1 | kimi-k2.6 [Kimi K2.6] | fixed | kimi-k2.6 [Kimi K2.6] | 1 | 1 | 0 | 0 | 0.957 | 0.917 | 1.000 | 0.958 | 1.000 | 1.000 | 1.000 |

## chlamydia_poc_test_50

**Title:** Rapid point of care test for detecting urogenital   Chlamydia trachomatis infection in nonpregnant women and men at reproductive age
**URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD011708.pub2/full
**Studies:** 50 | **Gold pass:** 19 | **Gold exclude:** 31

Metrics below are averaged only over scored runs with complete per-study decision coverage.

| Rank | Architecture | Gatekeeper Model | Orchestrator Policy | Orchestrator Model | Runs | Scored | Incomplete | Errors | F1 | Recall | Precision | Accuracy | Specificity | Parse Success | Coverage |
|------|--------------|------------------|---------------------|--------------------|------|--------|------------|--------|----|--------|-----------|----------|-------------|---------------|----------|
| 1 | loop_chunk_orchestrator_v1 | kimi-k2.6 [Kimi K2.6] | fixed | kimi-k2.6 [Kimi K2.6] | 1 | 1 | 0 | 0 | 0.882 | 0.789 | 1.000 | 0.920 | 1.000 | 1.000 | 1.000 |

## ovarian_cancer_diagnosis_92

**Title:** Menopausal status, ultrasound and biomarker tests in combination for the diagnosis of ovarian cancer in symptomatic women
**URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD011964.pub2/full
**Studies:** 92 | **Gold pass:** 45 | **Gold exclude:** 47

Metrics below are averaged only over scored runs with complete per-study decision coverage.

| Rank | Architecture | Gatekeeper Model | Orchestrator Policy | Orchestrator Model | Runs | Scored | Incomplete | Errors | F1 | Recall | Precision | Accuracy | Specificity | Parse Success | Coverage |
|------|--------------|------------------|---------------------|--------------------|------|--------|------------|--------|----|--------|-----------|----------|-------------|---------------|----------|
| 1 | loop_chunk_orchestrator_v1 | kimi-k2.6 [Kimi K2.6] | fixed | kimi-k2.6 [Kimi K2.6] | 1 | 1 | 0 | 0 | 0.867 | 0.867 | 0.867 | 0.870 | 0.872 | 1.000 | 1.000 |

## home_based_rehabilitation_183

**Title:** Factors that influence the provision of home‐based rehabilitation services for people needing rehabilitation: a qualitative evidence synthesis
**URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD014823/full
**Studies:** 183 | **Gold pass:** 138 | **Gold exclude:** 45

Metrics below are averaged only over scored runs with complete per-study decision coverage.

| Rank | Architecture | Gatekeeper Model | Orchestrator Policy | Orchestrator Model | Runs | Scored | Incomplete | Errors | F1 | Recall | Precision | Accuracy | Specificity | Parse Success | Coverage |
|------|--------------|------------------|---------------------|--------------------|------|--------|------------|--------|----|--------|-----------|----------|-------------|---------------|----------|
| 1 | loop_chunk_orchestrator_v1 | kimi-k2.6 [Kimi K2.6] | fixed | kimi-k2.6 [Kimi K2.6] | 1 | 1 | 0 | 0 | 0.722 | 0.565 | 1.000 | 0.672 | 1.000 | 1.000 | 1.000 |
