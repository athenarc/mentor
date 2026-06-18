# Incomplete Screening Totals Report

Source mode: `canonical`
Diagnostic source mode: `discover`
Canonical policy filter: exclude_label_0_5
Groups with incomplete runs: 4
Incomplete/unscored source runs: 10
Excluded incomplete model groups: 8

## screening_ladder / exclude_label_0_5 / loop_chunk_orchestrator_v1

Source runs: 40
Incomplete/unscored runs: 2
Excluded model groups: 2

### Missing SRs By Model Group

| Architecture | Gatekeeper Preset | Gatekeeper Model | Expected | Scored | Missing SRs | Source Summaries |
|--------------|-------------------|------------------|----------|--------|-------------|------------------|
| loop_chunk_orchestrator_v1 | nvidia_nemotron_3_super_120b_a12b | nvidia-nemotron-3-super-120b-a12b [NVIDIA Nemotron 3 Super 120B A12B] | 5 | 4 | pelvic_floor_training_100 | bastirr/output/screening_benchmarks/20260618_144851_screening_ladder_loop_chunked_nvidia_nemotron_3_super_120b_a12b/exclude_policy/summary.json |
| loop_chunk_orchestrator_v1 | qwen3.5_27b | qwen3.5-27b [Qwen 3.5 27B] | 5 | 4 | pelvic_floor_training_100 | bastirr/output/screening_benchmarks/20260618_123710_screening_ladder_loop_chunked_qwen3.5_27b/exclude_policy/summary.json |

### Incomplete/Unscored Source Runs

| Review | Run | Status | Scored | Coverage | Missing Decisions | Reason | Source Summary |
|--------|-----|--------|--------|----------|-------------------|--------|----------------|
| pelvic_floor_training_100 | 1 | incomplete | False | 0.750 | 25 | Parsed 75/100 unique decisions (missing=25, duplicate=0, invalid=0). | bastirr/output/screening_benchmarks/20260618_123710_screening_ladder_loop_chunked_qwen3.5_27b/exclude_policy/summary.json |
| pelvic_floor_training_100 | 1 | incomplete | False | 0.250 | 75 | Parsed 25/100 unique decisions (missing=75, duplicate=0, invalid=0). | bastirr/output/screening_benchmarks/20260618_144851_screening_ladder_loop_chunked_nvidia_nemotron_3_super_120b_a12b/exclude_policy/summary.json |

## screening_ladder_dev_exclude_balanced / exclude_label_0_5 / batch_orchestrator_v1

Source runs: 45
Incomplete/unscored runs: 3
Excluded model groups: 1

### Missing SRs By Model Group

| Architecture | Gatekeeper Preset | Gatekeeper Model | Expected | Scored | Missing SRs | Source Summaries |
|--------------|-------------------|------------------|----------|--------|-------------|------------------|
| batch_orchestrator_v1 | nvidia_nemotron_3_super_120b_a12b | nvidia-nemotron-3-super-120b-a12b [NVIDIA Nemotron 3 Super 120B A12B] | 5 | 2 | adhesive_capsulitis_50, desmopressin_transfusion_100, prom_feedback_194 | bastirr/output/screening_benchmarks/20260528_020539_screening_ladder_dev_exclude_balanced/exclude_policy/summary.json |

### Incomplete/Unscored Source Runs

| Review | Run | Status | Scored | Coverage | Missing Decisions | Reason | Source Summary |
|--------|-----|--------|--------|----------|-------------------|--------|----------------|
| adhesive_capsulitis_50 | 1 | incomplete | False | 0.000 | 50 | Parsed 0/50 unique decisions (missing=50, duplicate=0, invalid=0). | bastirr/output/screening_benchmarks/20260528_020539_screening_ladder_dev_exclude_balanced/exclude_policy/summary.json |
| desmopressin_transfusion_100 | 1 | incomplete | False | 0.000 | 100 | Parsed 0/100 unique decisions (missing=100, duplicate=0, invalid=0). | bastirr/output/screening_benchmarks/20260528_020539_screening_ladder_dev_exclude_balanced/exclude_policy/summary.json |
| prom_feedback_194 | 1 | incomplete | False | 0.000 | 194 | Parsed 0/194 unique decisions (missing=194, duplicate=0, invalid=0). | bastirr/output/screening_benchmarks/20260528_020539_screening_ladder_dev_exclude_balanced/exclude_policy/summary.json |

## screening_ladder_dev_exclude_balanced / exclude_label_0_5 / loop_chunk_orchestrator_v1

Source runs: 39
Incomplete/unscored runs: 3
Excluded model groups: 3

### Missing SRs By Model Group

| Architecture | Gatekeeper Preset | Gatekeeper Model | Expected | Scored | Missing SRs | Source Summaries |
|--------------|-------------------|------------------|----------|--------|-------------|------------------|
| loop_chunk_orchestrator_v1 | nvidia_nemotron_3_super_120b_a12b | nvidia-nemotron-3-super-120b-a12b [NVIDIA Nemotron 3 Super 120B A12B] | 5 | 3 | desmopressin_transfusion_100, prom_feedback_194 | bastirr/output/screening_benchmarks/20260618_214138_screening_ladder_dev_exclude_balanced_loop_chunked_nvidia_nemotron_3_super_120b_a12b/exclude_policy/summary.json |
| loop_chunk_orchestrator_v1 | qwen3.5_122b_a10b | qwen3.5-122b-a10b [Qwen 3.5 122B A10B] | 5 | 4 | desmopressin_transfusion_100 | bastirr/output/screening_benchmarks/20260618_111752_screening_ladder_dev_exclude_balanced_loop_chunked_qwen3.5_122b_a10b/exclude_policy/summary.json |
| loop_chunk_orchestrator_v1 | qwen3.5_27b | qwen3.5-27b [Qwen 3.5 27B] | 5 | 4 | prom_feedback_194 | bastirr/output/screening_benchmarks/20260618_132030_screening_ladder_dev_exclude_balanced_loop_chunked_qwen3.5_27b/exclude_policy/summary.json |

### Incomplete/Unscored Source Runs

| Review | Run | Status | Scored | Coverage | Missing Decisions | Reason | Source Summary |
|--------|-----|--------|--------|----------|-------------------|--------|----------------|
| desmopressin_transfusion_100 | 1 | incomplete | False | 0.750 | 25 | Parsed 75/100 unique decisions (missing=25, duplicate=0, invalid=0). | bastirr/output/screening_benchmarks/20260618_111752_screening_ladder_dev_exclude_balanced_loop_chunked_qwen3.5_122b_a10b/exclude_policy/summary.json |
| desmopressin_transfusion_100 | 1 | incomplete | False | 0.500 | 50 | Parsed 50/100 unique decisions (missing=50, duplicate=0, invalid=0). | bastirr/output/screening_benchmarks/20260618_214138_screening_ladder_dev_exclude_balanced_loop_chunked_nvidia_nemotron_3_super_120b_a12b/exclude_policy/summary.json |
| prom_feedback_194 | 1 | incomplete | False | 0.918 | 16 | Parsed 178/194 unique decisions (missing=16, duplicate=0, invalid=0). | bastirr/output/screening_benchmarks/20260618_214138_screening_ladder_dev_exclude_balanced_loop_chunked_nvidia_nemotron_3_super_120b_a12b/exclude_policy/summary.json |

## screening_ladder_dev_no_label_0_5 / exclude_label_0_5 / loop_chunk_orchestrator_v1

Source runs: 44
Incomplete/unscored runs: 2
Excluded model groups: 2

### Missing SRs By Model Group

| Architecture | Gatekeeper Preset | Gatekeeper Model | Expected | Scored | Missing SRs | Source Summaries |
|--------------|-------------------|------------------|----------|--------|-------------|------------------|
| loop_chunk_orchestrator_v1 | nvidia_nemotron_3_super_120b_a12b | nvidia-nemotron-3-super-120b-a12b [NVIDIA Nemotron 3 Super 120B A12B] | 5 | 4 | ovarian_cancer_diagnosis_92 | bastirr/output/screening_benchmarks/20260618_015513_screening_ladder_dev_no_label_0_5_loop_chunked_nvidia_nemotron_3_super_120b_a12b/exclude_policy/summary.json |
| loop_chunk_orchestrator_v1 | openai_gpt_oss_120b | gpt-oss-120b [OpenAI GPT-OSS 120B] | 5 | 3 | home_based_rehabilitation_183, ovarian_cancer_diagnosis_92 | bastirr/output/screening_benchmarks/20260618_040350_screening_ladder_dev_no_label_0_5_loop_chunked_openai_gpt_oss_120b/exclude_policy/summary.json |

### Incomplete/Unscored Source Runs

| Review | Run | Status | Scored | Coverage | Missing Decisions | Reason | Source Summary |
|--------|-----|--------|--------|----------|-------------------|--------|----------------|
| ovarian_cancer_diagnosis_92 | 1 | incomplete | False | 0.620 | 35 | Parsed 57/92 unique decisions (missing=35, duplicate=0, invalid=0). | bastirr/output/screening_benchmarks/20260618_015513_screening_ladder_dev_no_label_0_5_loop_chunked_nvidia_nemotron_3_super_120b_a12b/exclude_policy/summary.json |
| ovarian_cancer_diagnosis_92 | 1 | incomplete | False | 0.750 | 23 | Parsed 69/92 unique decisions (missing=23, duplicate=0, invalid=0). | bastirr/output/screening_benchmarks/20260618_040350_screening_ladder_dev_no_label_0_5_loop_chunked_openai_gpt_oss_120b/exclude_policy/summary.json |

