# Review-Level Screening Benchmark Leaderboard

This file compares model configurations within each review.

Gold label policy: `include_label_0_5`

## endometrial_progestagens_10

**Title:** Adjuvant progestagens for endometrial cancer
**URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD001040.pub2/full
**Studies:** 10 | **Gold pass:** 5 | **Gold exclude:** 5

Metrics below are averaged only over scored runs with complete per-study decision coverage.

| Rank | Architecture | Gatekeeper Model | Orchestrator Policy | Orchestrator Model | Runs | Scored | Incomplete | Errors | F1 | Recall | Precision | Accuracy | Specificity | Parse Success | Coverage |
|------|--------------|------------------|---------------------|--------------------|------|--------|------------|--------|----|--------|-----------|----------|-------------|---------------|----------|
| 1 | loop_chunk_orchestrator_v1 | nvidia-nemotron-3-super-120b-a12b [NVIDIA Nemotron 3 Super 120B A12B] | fixed | nvidia-nemotron-3-super-120b-a12b [NVIDIA Nemotron 3 Super 120B A12B] | 1 | 1 | 0 | 0 | 0.667 | 1.000 | 0.500 | 0.500 | 0.000 | 1.000 | 1.000 |

## tricyclic_depression_children_25

**Title:** Tricyclic drugs for depression in children and adolescents
**URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD002317.pub2/full
**Studies:** 25 | **Gold pass:** 15 | **Gold exclude:** 10

Metrics below are averaged only over scored runs with complete per-study decision coverage.

| Rank | Architecture | Gatekeeper Model | Orchestrator Policy | Orchestrator Model | Runs | Scored | Incomplete | Errors | F1 | Recall | Precision | Accuracy | Specificity | Parse Success | Coverage |
|------|--------------|------------------|---------------------|--------------------|------|--------|------------|--------|----|--------|-----------|----------|-------------|---------------|----------|
| 1 | loop_chunk_orchestrator_v1 | nvidia-nemotron-3-super-120b-a12b [NVIDIA Nemotron 3 Super 120B A12B] | fixed | nvidia-nemotron-3-super-120b-a12b [NVIDIA Nemotron 3 Super 120B A12B] | 1 | 1 | 0 | 0 | n/a | 0.000 | n/a | 0.400 | 1.000 | 1.000 | 1.000 |

## adhesive_capsulitis_50

**Title:** Manual therapy and exercise for adhesive capsulitis (frozen shoulder)
**URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD011275/full
**Studies:** 50 | **Gold pass:** 31 | **Gold exclude:** 19

Metrics below are averaged only over scored runs with complete per-study decision coverage.

| Rank | Architecture | Gatekeeper Model | Orchestrator Policy | Orchestrator Model | Runs | Scored | Incomplete | Errors | F1 | Recall | Precision | Accuracy | Specificity | Parse Success | Coverage |
|------|--------------|------------------|---------------------|--------------------|------|--------|------------|--------|----|--------|-----------|----------|-------------|---------------|----------|
| 1 | loop_chunk_orchestrator_v1 | nvidia-nemotron-3-super-120b-a12b [NVIDIA Nemotron 3 Super 120B A12B] | fixed | nvidia-nemotron-3-super-120b-a12b [NVIDIA Nemotron 3 Super 120B A12B] | 1 | 1 | 0 | 0 | 0.694 | 0.548 | 0.944 | 0.700 | 0.947 | 1.000 | 1.000 |

## desmopressin_transfusion_100

**Title:** Desmopressin use for minimising perioperative blood transfusion
**URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD001884.pub3/full
**Studies:** 100 | **Gold pass:** 72 | **Gold exclude:** 28

Metrics below are averaged only over scored runs with complete per-study decision coverage.

| Rank | Architecture | Gatekeeper Model | Orchestrator Policy | Orchestrator Model | Runs | Scored | Incomplete | Errors | F1 | Recall | Precision | Accuracy | Specificity | Parse Success | Coverage |
|------|--------------|------------------|---------------------|--------------------|------|--------|------------|--------|----|--------|-----------|----------|-------------|---------------|----------|
| 1 | loop_chunk_orchestrator_v1 | nvidia-nemotron-3-super-120b-a12b [NVIDIA Nemotron 3 Super 120B A12B] | fixed | nvidia-nemotron-3-super-120b-a12b [NVIDIA Nemotron 3 Super 120B A12B] | 1 | 1 | 0 | 0 | 0.785 | 0.736 | 0.841 | 0.710 | 0.643 | 1.000 | 1.000 |

## prom_feedback_194

**Title:** Routine provision of feedback from patient‐reported outcome measurements to healthcare providers and patients in clinical practice
**URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD011589.pub2/full
**Studies:** 194 | **Gold pass:** 148 | **Gold exclude:** 46

Metrics below are averaged only over scored runs with complete per-study decision coverage.

| Rank | Architecture | Gatekeeper Model | Orchestrator Policy | Orchestrator Model | Runs | Scored | Incomplete | Errors | F1 | Recall | Precision | Accuracy | Specificity | Parse Success | Coverage |
|------|--------------|------------------|---------------------|--------------------|------|--------|------------|--------|----|--------|-----------|----------|-------------|---------------|----------|
| 1 | loop_chunk_orchestrator_v1 | nvidia-nemotron-3-super-120b-a12b [NVIDIA Nemotron 3 Super 120B A12B] | fixed | nvidia-nemotron-3-super-120b-a12b [NVIDIA Nemotron 3 Super 120B A12B] | 1 | 1 | 0 | 0 | 0.647 | 0.520 | 0.856 | 0.567 | 0.717 | 1.000 | 1.000 |
