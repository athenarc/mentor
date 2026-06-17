# Horizontal Size-Band Summary

## small_10 (up to 15)

### Model Averages

| Rank | Architecture | Preset | Gatekeeper Model | Runs | Scored | Reviews | F1 | Recall | Precision | Accuracy |
|------|--------------|--------|------------------|------|--------|---------|----|--------|-----------|----------|
| 1 | batch_orchestrator_v1 | deepseek_v4_pro--xhigh | deepseek-v4-pro--xhigh [DeepSeek V4 Pro] | 3 | 3 | 3 | 0.878 | 0.794 | 1.000 | 0.867 |
| 2 | batch_orchestrator_v1 | nvidia_nemotron_3_super_120b_a12b | nvidia-nemotron-3-super-120b-a12b [NVIDIA Nemotron 3 Super 120B A12B] | 3 | 3 | 3 | 0.878 | 0.794 | 1.000 | 0.867 |
| 3 | batch_orchestrator_v1 | deepseek_v4_pro | deepseek-v4-pro [DeepSeek V4 Pro] | 2 | 2 | 2 | 0.844 | 0.733 | 1.000 | 0.850 |
| 4 | batch_orchestrator_v1 | openai_gpt5--xhigh | openai-gpt-5--xhigh [OpenAI GPT5] | 3 | 3 | 3 | 0.833 | 0.778 | 1.000 | 0.867 |
| 5 | batch_orchestrator_v1 | qwen3.5_27b | qwen3.5-27b [Qwen 3.5 27B] | 3 | 3 | 3 | 0.808 | 0.730 | 1.000 | 0.833 |
| 6 | batch_orchestrator_v1 | qwen3.5_122b_a10b | qwen3.5-122b-a10b [Qwen 3.5 122B A10B] | 3 | 3 | 3 | 0.808 | 0.730 | 1.000 | 0.833 |
| 7 | batch_orchestrator_v1 | kimi_k2.6 | kimi-k2.6 [Kimi K2.6] | 3 | 3 | 3 | 0.778 | 0.683 | 1.000 | 0.800 |
| 8 | batch_orchestrator_v1 | openai_gpt5 | openai-gpt-5 [OpenAI GPT5] | 2 | 2 | 2 | 0.750 | 0.667 | 1.000 | 0.800 |
| 9 | batch_orchestrator_v1 | openai_gpt_oss_120b | gpt-oss-120b [OpenAI GPT-OSS 120B] | 3 | 3 | 3 | 0.724 | 0.597 | 1.000 | 0.767 |
| 10 | batch_orchestrator_v1 | mistral_medium_3.5 | mistral-medium-3.5 [Mistral Medium 3.5] | 1 | 1 | 1 | 0.500 | 0.333 | 1.000 | 0.600 |
| 11 | batch_orchestrator_v1 | openai_gpt5.4_mini | openai-gpt-5.4-mini [OpenAI GPT-5.4 Mini] | 1 | 1 | 1 | 0.500 | 0.333 | 1.000 | 0.600 |

### Review Rows

| Review | Suite | Studies | Architecture | Preset | Gatekeeper Model | Runs | Scored | F1 | Recall | Precision | Accuracy |
|--------|-------|---------|--------------|--------|------------------|------|--------|----|--------|-----------|----------|
| endometrial_progestagens_10 | screening_ladder_dev_exclude_balanced | 10 | batch_orchestrator_v1 | qwen3.5_27b | qwen3.5-27b [Qwen 3.5 27B] | 1 | 1 | 1.000 | 1.000 | 1.000 | 1.000 |
| endometrial_progestagens_10 | screening_ladder_dev_no_label_0_5_v2 | 10 | batch_orchestrator_v1 | kimi_k2.6 | kimi-k2.6 [Kimi K2.6] | 1 | 1 | 1.000 | 1.000 | 1.000 | 1.000 |
| endometrial_progestagens_10 | screening_ladder_dev_exclude_balanced | 10 | batch_orchestrator_v1 | openai_gpt5 | openai-gpt-5 [OpenAI GPT5] | 1 | 1 | 1.000 | 1.000 | 1.000 | 1.000 |
| endometrial_progestagens_10 | screening_ladder_dev_no_label_0_5_v2 | 10 | batch_orchestrator_v1 | deepseek_v4_pro--xhigh | deepseek-v4-pro--xhigh [DeepSeek V4 Pro] | 1 | 1 | 1.000 | 1.000 | 1.000 | 1.000 |
| endometrial_progestagens_10 | screening_ladder_dev_no_label_0_5_v2 | 10 | batch_orchestrator_v1 | openai_gpt5--xhigh | openai-gpt-5--xhigh [OpenAI GPT5] | 1 | 1 | 1.000 | 1.000 | 1.000 | 1.000 |
| endometrial_progestagens_10 | screening_ladder_dev_exclude_balanced | 10 | batch_orchestrator_v1 | qwen3.5_122b_a10b | qwen3.5-122b-a10b [Qwen 3.5 122B A10B] | 1 | 1 | 1.000 | 1.000 | 1.000 | 1.000 |
| endometrial_progestagens_10 | screening_ladder_dev_exclude_balanced | 10 | batch_orchestrator_v1 | nvidia_nemotron_3_super_120b_a12b | nvidia-nemotron-3-super-120b-a12b [NVIDIA Nemotron 3 Super 120B A12B] | 1 | 1 | 1.000 | 1.000 | 1.000 | 1.000 |
| endometrial_progestagens_10 | screening_ladder_dev_exclude_balanced | 10 | batch_orchestrator_v1 | deepseek_v4_pro | deepseek-v4-pro [DeepSeek V4 Pro] | 1 | 1 | 0.889 | 0.800 | 1.000 | 0.900 |
| endometrial_progestagens_10 | screening_ladder_dev_exclude_balanced | 10 | batch_orchestrator_v1 | openai_gpt_oss_120b | gpt-oss-120b [OpenAI GPT-OSS 120B] | 1 | 1 | 0.750 | 0.600 | 1.000 | 0.800 |
| stroke_theophylline_10 | screening_ladder | 10 | batch_orchestrator_v1 | deepseek_v4_pro | deepseek-v4-pro [DeepSeek V4 Pro] | 1 | 1 | 0.800 | 0.667 | 1.000 | 0.800 |
| stroke_theophylline_10 | screening_ladder | 10 | batch_orchestrator_v1 | deepseek_v4_pro--xhigh | deepseek-v4-pro--xhigh [DeepSeek V4 Pro] | 1 | 1 | 0.800 | 0.667 | 1.000 | 0.800 |
| stroke_theophylline_10 | screening_ladder | 10 | batch_orchestrator_v1 | nvidia_nemotron_3_super_120b_a12b | nvidia-nemotron-3-super-120b-a12b [NVIDIA Nemotron 3 Super 120B A12B] | 1 | 1 | 0.800 | 0.667 | 1.000 | 0.800 |
| stroke_theophylline_10 | screening_ladder | 10 | batch_orchestrator_v1 | openai_gpt5 | openai-gpt-5 [OpenAI GPT5] | 1 | 1 | 0.500 | 0.333 | 1.000 | 0.600 |
| stroke_theophylline_10 | screening_ladder | 10 | batch_orchestrator_v1 | kimi_k2.6 | kimi-k2.6 [Kimi K2.6] | 1 | 1 | 0.500 | 0.333 | 1.000 | 0.600 |
| stroke_theophylline_10 | screening_ladder | 10 | batch_orchestrator_v1 | qwen3.5_27b | qwen3.5-27b [Qwen 3.5 27B] | 1 | 1 | 0.500 | 0.333 | 1.000 | 0.600 |
| stroke_theophylline_10 | screening_ladder | 10 | batch_orchestrator_v1 | mistral_medium_3.5 | mistral-medium-3.5 [Mistral Medium 3.5] | 1 | 1 | 0.500 | 0.333 | 1.000 | 0.600 |
| stroke_theophylline_10 | screening_ladder | 10 | batch_orchestrator_v1 | openai_gpt5.4_mini | openai-gpt-5.4-mini [OpenAI GPT-5.4 Mini] | 1 | 1 | 0.500 | 0.333 | 1.000 | 0.600 |
| stroke_theophylline_10 | screening_ladder | 10 | batch_orchestrator_v1 | qwen3.5_122b_a10b | qwen3.5-122b-a10b [Qwen 3.5 122B A10B] | 1 | 1 | 0.500 | 0.333 | 1.000 | 0.600 |
| stroke_theophylline_10 | screening_ladder | 10 | batch_orchestrator_v1 | openai_gpt5--xhigh | openai-gpt-5--xhigh [OpenAI GPT5] | 1 | 1 | 0.500 | 0.333 | 1.000 | 0.600 |
| stroke_theophylline_10 | screening_ladder | 10 | batch_orchestrator_v1 | openai_gpt_oss_120b | gpt-oss-120b [OpenAI GPT-OSS 120B] | 1 | 1 | 0.500 | 0.333 | 1.000 | 0.600 |
| surgical_termination_10 | screening_ladder_dev_no_label_0_5 | 10 | batch_orchestrator_v1 | openai_gpt5--xhigh | openai-gpt-5--xhigh [OpenAI GPT5] | 1 | 1 | 1.000 | 1.000 | 1.000 | 1.000 |
| surgical_termination_10 | screening_ladder_dev_no_label_0_5 | 10 | batch_orchestrator_v1 | qwen3.5_122b_a10b | qwen3.5-122b-a10b [Qwen 3.5 122B A10B] | 1 | 1 | 0.923 | 0.857 | 1.000 | 0.900 |
| surgical_termination_10 | screening_ladder_dev_no_label_0_5 | 10 | batch_orchestrator_v1 | qwen3.5_27b | qwen3.5-27b [Qwen 3.5 27B] | 1 | 1 | 0.923 | 0.857 | 1.000 | 0.900 |
| surgical_termination_10 | screening_ladder_dev_no_label_0_5 | 10 | batch_orchestrator_v1 | openai_gpt_oss_120b | gpt-oss-120b [OpenAI GPT-OSS 120B] | 1 | 1 | 0.923 | 0.857 | 1.000 | 0.900 |
| surgical_termination_10 | screening_ladder_dev_no_label_0_5 | 10 | batch_orchestrator_v1 | kimi_k2.6 | kimi-k2.6 [Kimi K2.6] | 1 | 1 | 0.833 | 0.714 | 1.000 | 0.800 |
| surgical_termination_10 | screening_ladder_dev_no_label_0_5 | 10 | batch_orchestrator_v1 | deepseek_v4_pro--xhigh | deepseek-v4-pro--xhigh [DeepSeek V4 Pro] | 1 | 1 | 0.833 | 0.714 | 1.000 | 0.800 |
| surgical_termination_10 | screening_ladder_dev_no_label_0_5 | 10 | batch_orchestrator_v1 | nvidia_nemotron_3_super_120b_a12b | nvidia-nemotron-3-super-120b-a12b [NVIDIA Nemotron 3 Super 120B A12B] | 1 | 1 | 0.833 | 0.714 | 1.000 | 0.800 |

## lower_mid_25 (16-35)

### Model Averages

| Rank | Architecture | Preset | Gatekeeper Model | Runs | Scored | Reviews | F1 | Recall | Precision | Accuracy |
|------|--------------|--------|------------------|------|--------|---------|----|--------|-----------|----------|
| 1 | batch_orchestrator_v1 | qwen3.5_122b_a10b | qwen3.5-122b-a10b [Qwen 3.5 122B A10B] | 3 | 3 | 3 | 0.979 | 0.978 | 0.981 | 0.973 |
| 2 | batch_orchestrator_v1 | openai_gpt5.4_mini | openai-gpt-5.4-mini [OpenAI GPT-5.4 Mini] | 1 | 1 | 1 | 0.971 | 1.000 | 0.944 | 0.960 |
| 3 | batch_orchestrator_v1 | nvidia_nemotron_3_super_120b_a12b | nvidia-nemotron-3-super-120b-a12b [NVIDIA Nemotron 3 Super 120B A12B] | 3 | 3 | 3 | 0.933 | 0.894 | 0.979 | 0.920 |
| 4 | batch_orchestrator_v1 | qwen3.5_27b | qwen3.5-27b [Qwen 3.5 27B] | 3 | 3 | 3 | 0.904 | 0.844 | 0.979 | 0.893 |
| 5 | batch_orchestrator_v1 | openai_gpt_oss_120b | gpt-oss-120b [OpenAI GPT-OSS 120B] | 3 | 3 | 3 | 0.889 | 0.822 | 0.979 | 0.879 |
| 6 | batch_orchestrator_v1 | kimi_k2.6 | kimi-k2.6 [Kimi K2.6] | 4 | 4 | 4 | 0.875 | 0.814 | 0.963 | 0.870 |
| 7 | batch_orchestrator_v1 | openai_gpt5 | openai-gpt-5 [OpenAI GPT5] | 2 | 2 | 2 | 0.871 | 0.804 | 0.971 | 0.860 |
| 8 | batch_orchestrator_v1 | openai_gpt5--xhigh | openai-gpt-5--xhigh [OpenAI GPT5] | 4 | 4 | 4 | 0.868 | 0.835 | 0.933 | 0.861 |
| 9 | batch_orchestrator_v1 | deepseek_v4_pro--xhigh | deepseek-v4-pro--xhigh [DeepSeek V4 Pro] | 4 | 4 | 4 | 0.865 | 0.814 | 0.945 | 0.861 |
| 10 | batch_orchestrator_v1 | deepseek_v4_pro | deepseek-v4-pro [DeepSeek V4 Pro] | 2 | 2 | 2 | 0.794 | 0.682 | 0.964 | 0.780 |
| 11 | batch_orchestrator_v1 | mistral_medium_3.5 | mistral-medium-3.5 [Mistral Medium 3.5] | 1 | 1 | 1 | 0.381 | 0.235 | 1.000 | 0.480 |

### Review Rows

| Review | Suite | Studies | Architecture | Preset | Gatekeeper Model | Runs | Scored | F1 | Recall | Precision | Accuracy |
|--------|-------|---------|--------------|--------|------------------|------|--------|----|--------|-----------|----------|
| advanced_endometrial_carcinoma_24 | screening_ladder_dev_no_label_0_5 | 24 | batch_orchestrator_v1 | qwen3.5_122b_a10b | qwen3.5-122b-a10b [Qwen 3.5 122B A10B] | 1 | 1 | 1.000 | 1.000 | 1.000 | 1.000 |
| advanced_endometrial_carcinoma_24 | screening_ladder_dev_no_label_0_5 | 24 | batch_orchestrator_v1 | nvidia_nemotron_3_super_120b_a12b | nvidia-nemotron-3-super-120b-a12b [NVIDIA Nemotron 3 Super 120B A12B] | 1 | 1 | 1.000 | 1.000 | 1.000 | 1.000 |
| advanced_endometrial_carcinoma_24 | screening_ladder_dev_no_label_0_5 | 24 | batch_orchestrator_v1 | kimi_k2.6 | kimi-k2.6 [Kimi K2.6] | 1 | 1 | 0.957 | 0.917 | 1.000 | 0.958 |
| advanced_endometrial_carcinoma_24 | screening_ladder_dev_no_label_0_5 | 24 | batch_orchestrator_v1 | openai_gpt5--xhigh | openai-gpt-5--xhigh [OpenAI GPT5] | 1 | 1 | 0.957 | 0.917 | 1.000 | 0.958 |
| advanced_endometrial_carcinoma_24 | screening_ladder_dev_no_label_0_5 | 24 | batch_orchestrator_v1 | qwen3.5_27b | qwen3.5-27b [Qwen 3.5 27B] | 1 | 1 | 0.957 | 0.917 | 1.000 | 0.958 |
| advanced_endometrial_carcinoma_24 | screening_ladder_dev_no_label_0_5 | 24 | batch_orchestrator_v1 | deepseek_v4_pro--xhigh | deepseek-v4-pro--xhigh [DeepSeek V4 Pro] | 1 | 1 | 0.957 | 0.917 | 1.000 | 0.958 |
| advanced_endometrial_carcinoma_24 | screening_ladder_dev_no_label_0_5 | 24 | batch_orchestrator_v1 | openai_gpt_oss_120b | gpt-oss-120b [OpenAI GPT-OSS 120B] | 1 | 1 | 0.957 | 0.917 | 1.000 | 0.958 |
| alopecia_areata_25 | screening_ladder | 25 | batch_orchestrator_v1 | openai_gpt5.4_mini | openai-gpt-5.4-mini [OpenAI GPT-5.4 Mini] | 1 | 1 | 0.971 | 1.000 | 0.944 | 0.960 |
| alopecia_areata_25 | screening_ladder | 25 | batch_orchestrator_v1 | qwen3.5_122b_a10b | qwen3.5-122b-a10b [Qwen 3.5 122B A10B] | 1 | 1 | 0.971 | 1.000 | 0.944 | 0.960 |
| alopecia_areata_25 | screening_ladder | 25 | batch_orchestrator_v1 | openai_gpt5 | openai-gpt-5 [OpenAI GPT5] | 1 | 1 | 0.941 | 0.941 | 0.941 | 0.920 |
| alopecia_areata_25 | screening_ladder | 25 | batch_orchestrator_v1 | qwen3.5_27b | qwen3.5-27b [Qwen 3.5 27B] | 1 | 1 | 0.909 | 0.882 | 0.938 | 0.880 |
| alopecia_areata_25 | screening_ladder | 25 | batch_orchestrator_v1 | openai_gpt_oss_120b | gpt-oss-120b [OpenAI GPT-OSS 120B] | 1 | 1 | 0.909 | 0.882 | 0.938 | 0.880 |
| alopecia_areata_25 | screening_ladder | 25 | batch_orchestrator_v1 | nvidia_nemotron_3_super_120b_a12b | nvidia-nemotron-3-super-120b-a12b [NVIDIA Nemotron 3 Super 120B A12B] | 1 | 1 | 0.909 | 0.882 | 0.938 | 0.880 |
| alopecia_areata_25 | screening_ladder | 25 | batch_orchestrator_v1 | kimi_k2.6 | kimi-k2.6 [Kimi K2.6] | 1 | 1 | 0.875 | 0.824 | 0.933 | 0.840 |
| alopecia_areata_25 | screening_ladder | 25 | batch_orchestrator_v1 | openai_gpt5--xhigh | openai-gpt-5--xhigh [OpenAI GPT5] | 1 | 1 | 0.875 | 0.824 | 0.933 | 0.840 |
| alopecia_areata_25 | screening_ladder | 25 | batch_orchestrator_v1 | deepseek_v4_pro--xhigh | deepseek-v4-pro--xhigh [DeepSeek V4 Pro] | 1 | 1 | 0.875 | 0.824 | 0.933 | 0.840 |
| alopecia_areata_25 | screening_ladder | 25 | batch_orchestrator_v1 | deepseek_v4_pro | deepseek-v4-pro [DeepSeek V4 Pro] | 1 | 1 | 0.839 | 0.765 | 0.929 | 0.800 |
| alopecia_areata_25 | screening_ladder | 25 | batch_orchestrator_v1 | mistral_medium_3.5 | mistral-medium-3.5 [Mistral Medium 3.5] | 1 | 1 | 0.381 | 0.235 | 1.000 | 0.480 |
| tricyclic_depression_children_25 | screening_ladder_dev_exclude_balanced | 25 | batch_orchestrator_v1 | qwen3.5_122b_a10b | qwen3.5-122b-a10b [Qwen 3.5 122B A10B] | 1 | 1 | 0.966 | 0.933 | 1.000 | 0.960 |
| tricyclic_depression_children_25 | screening_ladder_dev_exclude_balanced | 25 | batch_orchestrator_v1 | nvidia_nemotron_3_super_120b_a12b | nvidia-nemotron-3-super-120b-a12b [NVIDIA Nemotron 3 Super 120B A12B] | 1 | 1 | 0.889 | 0.800 | 1.000 | 0.880 |
| tricyclic_depression_children_25 | screening_ladder_dev_exclude_balanced | 25 | batch_orchestrator_v1 | qwen3.5_27b | qwen3.5-27b [Qwen 3.5 27B] | 1 | 1 | 0.846 | 0.733 | 1.000 | 0.840 |
| tricyclic_depression_children_25 | screening_ladder_dev_exclude_balanced | 25 | batch_orchestrator_v1 | openai_gpt5 | openai-gpt-5 [OpenAI GPT5] | 1 | 1 | 0.800 | 0.667 | 1.000 | 0.800 |
| tricyclic_depression_children_25 | screening_ladder_dev_exclude_balanced | 25 | batch_orchestrator_v1 | openai_gpt_oss_120b | gpt-oss-120b [OpenAI GPT-OSS 120B] | 1 | 1 | 0.800 | 0.667 | 1.000 | 0.800 |
| tricyclic_depression_children_25 | screening_ladder_dev_exclude_balanced | 25 | batch_orchestrator_v1 | deepseek_v4_pro | deepseek-v4-pro [DeepSeek V4 Pro] | 1 | 1 | 0.750 | 0.600 | 1.000 | 0.760 |
| tricyclic_depression_children_25 | screening_ladder_dev_exclude_balanced | 25 | batch_orchestrator_v1 | kimi_k2.6 | kimi-k2.6 [Kimi K2.6] | 1 | 1 | 0.750 | 0.600 | 1.000 | 0.760 |
| tricyclic_depression_children_25 | screening_ladder_dev_exclude_balanced | 25 | batch_orchestrator_v1 | deepseek_v4_pro--xhigh | deepseek-v4-pro--xhigh [DeepSeek V4 Pro] | 1 | 1 | 0.750 | 0.600 | 1.000 | 0.760 |
| tricyclic_depression_children_25 | screening_ladder_dev_exclude_balanced | 25 | batch_orchestrator_v1 | openai_gpt5--xhigh | openai-gpt-5--xhigh [OpenAI GPT5] | 1 | 1 | 0.750 | 0.600 | 1.000 | 0.760 |
| glucocorticoids_rheumatoid_26 | screening_ladder_dev_no_label_0_5_v2 | 26 | batch_orchestrator_v1 | kimi_k2.6 | kimi-k2.6 [Kimi K2.6] | 1 | 1 | 0.917 | 0.917 | 0.917 | 0.923 |
| glucocorticoids_rheumatoid_26 | screening_ladder_dev_no_label_0_5_v2 | 26 | batch_orchestrator_v1 | openai_gpt5--xhigh | openai-gpt-5--xhigh [OpenAI GPT5] | 1 | 1 | 0.889 | 1.000 | 0.800 | 0.885 |
| glucocorticoids_rheumatoid_26 | screening_ladder_dev_no_label_0_5_v2 | 26 | batch_orchestrator_v1 | deepseek_v4_pro--xhigh | deepseek-v4-pro--xhigh [DeepSeek V4 Pro] | 1 | 1 | 0.880 | 0.917 | 0.846 | 0.885 |

## mid_50 (36-65)

### Model Averages

| Rank | Architecture | Preset | Gatekeeper Model | Runs | Scored | Reviews | F1 | Recall | Precision | Accuracy |
|------|--------------|--------|------------------|------|--------|---------|----|--------|-----------|----------|
| 1 | batch_orchestrator_v1 | qwen3.5_27b | qwen3.5-27b [Qwen 3.5 27B] | 3 | 3 | 3 | 0.953 | 0.910 | 1.000 | 0.953 |
| 2 | batch_orchestrator_v1 | qwen3.5_122b_a10b | qwen3.5-122b-a10b [Qwen 3.5 122B A10B] | 3 | 3 | 3 | 0.950 | 0.906 | 1.000 | 0.947 |
| 3 | batch_orchestrator_v1 | mistral_medium_3.5 | mistral-medium-3.5 [Mistral Medium 3.5] | 1 | 1 | 1 | 0.947 | 0.900 | 1.000 | 0.940 |
| 4 | batch_orchestrator_v1 | deepseek_v4_pro | deepseek-v4-pro [DeepSeek V4 Pro] | 2 | 2 | 2 | 0.930 | 0.869 | 1.000 | 0.920 |
| 5 | batch_orchestrator_v1 | openai_gpt5.4_mini | openai-gpt-5.4-mini [OpenAI GPT-5.4 Mini] | 1 | 1 | 1 | 0.929 | 0.867 | 1.000 | 0.920 |
| 6 | batch_orchestrator_v1 | kimi_k2.6 | kimi-k2.6 [Kimi K2.6] | 4 | 4 | 4 | 0.926 | 0.868 | 1.000 | 0.925 |
| 7 | batch_orchestrator_v1 | openai_gpt_oss_120b | gpt-oss-120b [OpenAI GPT-OSS 120B] | 3 | 3 | 3 | 0.910 | 0.840 | 1.000 | 0.907 |
| 8 | batch_orchestrator_v1 | openai_gpt5 | openai-gpt-5 [OpenAI GPT5] | 2 | 2 | 2 | 0.910 | 0.837 | 1.000 | 0.900 |
| 9 | batch_orchestrator_v1 | nvidia_nemotron_3_super_120b_a12b | nvidia-nemotron-3-super-120b-a12b [NVIDIA Nemotron 3 Super 120B A12B] | 3 | 2 | 3 | 0.906 | 0.831 | 1.000 | 0.910 |
| 10 | batch_orchestrator_v1 | openai_gpt5--xhigh | openai-gpt-5--xhigh [OpenAI GPT5] | 4 | 4 | 4 | 0.792 | 0.717 | 1.000 | 0.896 |
| 11 | batch_orchestrator_v1 | deepseek_v4_pro--xhigh | deepseek-v4-pro--xhigh [DeepSeek V4 Pro] | 4 | 4 | 4 | 0.772 | 0.682 | 1.000 | 0.881 |

### Review Rows

| Review | Suite | Studies | Architecture | Preset | Gatekeeper Model | Runs | Scored | F1 | Recall | Precision | Accuracy |
|--------|-------|---------|--------------|--------|------------------|------|--------|----|--------|-----------|----------|
| adhesive_capsulitis_50 | screening_ladder_dev_exclude_balanced | 50 | batch_orchestrator_v1 | qwen3.5_27b | qwen3.5-27b [Qwen 3.5 27B] | 1 | 1 | 0.949 | 0.903 | 1.000 | 0.940 |
| adhesive_capsulitis_50 | screening_ladder_dev_exclude_balanced | 50 | batch_orchestrator_v1 | qwen3.5_122b_a10b | qwen3.5-122b-a10b [Qwen 3.5 122B A10B] | 1 | 1 | 0.949 | 0.903 | 1.000 | 0.940 |
| adhesive_capsulitis_50 | screening_ladder_dev_exclude_balanced | 50 | batch_orchestrator_v1 | deepseek_v4_pro | deepseek-v4-pro [DeepSeek V4 Pro] | 1 | 1 | 0.931 | 0.871 | 1.000 | 0.920 |
| adhesive_capsulitis_50 | screening_ladder_dev_exclude_balanced | 50 | batch_orchestrator_v1 | openai_gpt_oss_120b | gpt-oss-120b [OpenAI GPT-OSS 120B] | 1 | 1 | 0.912 | 0.839 | 1.000 | 0.900 |
| adhesive_capsulitis_50 | screening_ladder_dev_exclude_balanced | 50 | batch_orchestrator_v1 | deepseek_v4_pro--xhigh | deepseek-v4-pro--xhigh [DeepSeek V4 Pro] | 1 | 1 | 0.912 | 0.839 | 1.000 | 0.900 |
| adhesive_capsulitis_50 | screening_ladder_dev_exclude_balanced | 50 | batch_orchestrator_v1 | openai_gpt5--xhigh | openai-gpt-5--xhigh [OpenAI GPT5] | 1 | 1 | 0.893 | 0.806 | 1.000 | 0.880 |
| adhesive_capsulitis_50 | screening_ladder_dev_exclude_balanced | 50 | batch_orchestrator_v1 | openai_gpt5 | openai-gpt-5 [OpenAI GPT5] | 1 | 1 | 0.873 | 0.774 | 1.000 | 0.860 |
| adhesive_capsulitis_50 | screening_ladder_dev_exclude_balanced | 50 | batch_orchestrator_v1 | kimi_k2.6 | kimi-k2.6 [Kimi K2.6] | 1 | 1 | 0.830 | 0.710 | 1.000 | 0.820 |
| adhesive_capsulitis_50 | screening_ladder_dev_exclude_balanced | 50 | batch_orchestrator_v1 | nvidia_nemotron_3_super_120b_a12b | nvidia-nemotron-3-super-120b-a12b [NVIDIA Nemotron 3 Super 120B A12B] | 1 | 0 | n/a | n/a | n/a | n/a |
| chlamydia_poc_test_50 | screening_ladder_dev_no_label_0_5 | 50 | batch_orchestrator_v1 | openai_gpt5--xhigh | openai-gpt-5--xhigh [OpenAI GPT5] | 1 | 1 | 0.973 | 0.947 | 1.000 | 0.980 |
| chlamydia_poc_test_50 | screening_ladder_dev_no_label_0_5 | 50 | batch_orchestrator_v1 | qwen3.5_122b_a10b | qwen3.5-122b-a10b [Qwen 3.5 122B A10B] | 1 | 1 | 0.973 | 0.947 | 1.000 | 0.980 |
| chlamydia_poc_test_50 | screening_ladder_dev_no_label_0_5 | 50 | batch_orchestrator_v1 | openai_gpt_oss_120b | gpt-oss-120b [OpenAI GPT-OSS 120B] | 1 | 1 | 0.973 | 0.947 | 1.000 | 0.980 |
| chlamydia_poc_test_50 | screening_ladder_dev_no_label_0_5 | 50 | batch_orchestrator_v1 | kimi_k2.6 | kimi-k2.6 [Kimi K2.6] | 1 | 1 | 0.944 | 0.895 | 1.000 | 0.960 |
| chlamydia_poc_test_50 | screening_ladder_dev_no_label_0_5 | 50 | batch_orchestrator_v1 | qwen3.5_27b | qwen3.5-27b [Qwen 3.5 27B] | 1 | 1 | 0.944 | 0.895 | 1.000 | 0.960 |
| chlamydia_poc_test_50 | screening_ladder_dev_no_label_0_5 | 50 | batch_orchestrator_v1 | nvidia_nemotron_3_super_120b_a12b | nvidia-nemotron-3-super-120b-a12b [NVIDIA Nemotron 3 Super 120B A12B] | 1 | 1 | 0.944 | 0.895 | 1.000 | 0.960 |
| chlamydia_poc_test_50 | screening_ladder_dev_no_label_0_5 | 50 | batch_orchestrator_v1 | deepseek_v4_pro--xhigh | deepseek-v4-pro--xhigh [DeepSeek V4 Pro] | 1 | 1 | 0.914 | 0.842 | 1.000 | 0.940 |
| iud_insertion_pain_50 | screening_ladder | 50 | batch_orchestrator_v1 | qwen3.5_27b | qwen3.5-27b [Qwen 3.5 27B] | 1 | 1 | 0.966 | 0.933 | 1.000 | 0.960 |
| iud_insertion_pain_50 | screening_ladder | 50 | batch_orchestrator_v1 | openai_gpt5 | openai-gpt-5 [OpenAI GPT5] | 1 | 1 | 0.947 | 0.900 | 1.000 | 0.940 |
| iud_insertion_pain_50 | screening_ladder | 50 | batch_orchestrator_v1 | mistral_medium_3.5 | mistral-medium-3.5 [Mistral Medium 3.5] | 1 | 1 | 0.947 | 0.900 | 1.000 | 0.940 |
| iud_insertion_pain_50 | screening_ladder | 50 | batch_orchestrator_v1 | openai_gpt5--xhigh | openai-gpt-5--xhigh [OpenAI GPT5] | 1 | 1 | 0.947 | 0.900 | 1.000 | 0.940 |
| iud_insertion_pain_50 | screening_ladder | 50 | batch_orchestrator_v1 | deepseek_v4_pro | deepseek-v4-pro [DeepSeek V4 Pro] | 1 | 1 | 0.929 | 0.867 | 1.000 | 0.920 |
| iud_insertion_pain_50 | screening_ladder | 50 | batch_orchestrator_v1 | kimi_k2.6 | kimi-k2.6 [Kimi K2.6] | 1 | 1 | 0.929 | 0.867 | 1.000 | 0.920 |
| iud_insertion_pain_50 | screening_ladder | 50 | batch_orchestrator_v1 | openai_gpt5.4_mini | openai-gpt-5.4-mini [OpenAI GPT-5.4 Mini] | 1 | 1 | 0.929 | 0.867 | 1.000 | 0.920 |
| iud_insertion_pain_50 | screening_ladder | 50 | batch_orchestrator_v1 | qwen3.5_122b_a10b | qwen3.5-122b-a10b [Qwen 3.5 122B A10B] | 1 | 1 | 0.929 | 0.867 | 1.000 | 0.920 |
| iud_insertion_pain_50 | screening_ladder | 50 | batch_orchestrator_v1 | deepseek_v4_pro--xhigh | deepseek-v4-pro--xhigh [DeepSeek V4 Pro] | 1 | 1 | 0.909 | 0.833 | 1.000 | 0.900 |
| iud_insertion_pain_50 | screening_ladder | 50 | batch_orchestrator_v1 | nvidia_nemotron_3_super_120b_a12b | nvidia-nemotron-3-super-120b-a12b [NVIDIA Nemotron 3 Super 120B A12B] | 1 | 1 | 0.868 | 0.767 | 1.000 | 0.860 |
| iud_insertion_pain_50 | screening_ladder | 50 | batch_orchestrator_v1 | openai_gpt_oss_120b | gpt-oss-120b [OpenAI GPT-OSS 120B] | 1 | 1 | 0.846 | 0.733 | 1.000 | 0.840 |
| vitamin_d_ckd_not_dialysis_51 | screening_ladder_dev_no_label_0_5_v2 | 51 | batch_orchestrator_v1 | kimi_k2.6 | kimi-k2.6 [Kimi K2.6] | 1 | 1 | 1.000 | 1.000 | 1.000 | 1.000 |
| vitamin_d_ckd_not_dialysis_51 | screening_ladder_dev_no_label_0_5_v2 | 51 | batch_orchestrator_v1 | openai_gpt5--xhigh | openai-gpt-5--xhigh [OpenAI GPT5] | 1 | 1 | 0.353 | 0.214 | 1.000 | 0.784 |
| vitamin_d_ckd_not_dialysis_51 | screening_ladder_dev_no_label_0_5_v2 | 51 | batch_orchestrator_v1 | deepseek_v4_pro--xhigh | deepseek-v4-pro--xhigh [DeepSeek V4 Pro] | 1 | 1 | 0.353 | 0.214 | 1.000 | 0.784 |

## upper_mid_100 (66-100)

### Model Averages

| Rank | Architecture | Preset | Gatekeeper Model | Runs | Scored | Reviews | F1 | Recall | Precision | Accuracy |
|------|--------------|--------|------------------|------|--------|---------|----|--------|-----------|----------|
| 1 | batch_orchestrator_v1 | qwen3.5_122b_a10b | qwen3.5-122b-a10b [Qwen 3.5 122B A10B] | 3 | 3 | 3 | 0.894 | 0.865 | 0.939 | 0.894 |
| 2 | batch_orchestrator_v1 | deepseek_v4_pro | deepseek-v4-pro [DeepSeek V4 Pro] | 2 | 2 | 2 | 0.843 | 0.729 | 1.000 | 0.840 |
| 3 | batch_orchestrator_v1 | openai_gpt5 | openai-gpt-5 [OpenAI GPT5] | 2 | 2 | 2 | 0.842 | 0.729 | 1.000 | 0.845 |
| 4 | batch_orchestrator_v1 | deepseek_v4_pro--xhigh | deepseek-v4-pro--xhigh [DeepSeek V4 Pro] | 4 | 4 | 4 | 0.840 | 0.764 | 0.948 | 0.850 |
| 5 | batch_orchestrator_v1 | qwen3.5_27b | qwen3.5-27b [Qwen 3.5 27B] | 3 | 3 | 3 | 0.834 | 0.773 | 0.949 | 0.844 |
| 6 | batch_orchestrator_v1 | openai_gpt_oss_120b | gpt-oss-120b [OpenAI GPT-OSS 120B] | 3 | 3 | 3 | 0.834 | 0.779 | 0.953 | 0.861 |
| 7 | batch_orchestrator_v1 | openai_gpt5--xhigh | openai-gpt-5--xhigh [OpenAI GPT5] | 4 | 4 | 4 | 0.821 | 0.736 | 0.945 | 0.836 |
| 8 | batch_orchestrator_v1 | kimi_k2.6 | kimi-k2.6 [Kimi K2.6] | 4 | 4 | 4 | 0.793 | 0.712 | 0.944 | 0.830 |
| 9 | batch_orchestrator_v1 | mistral_medium_3.5 | mistral-medium-3.5 [Mistral Medium 3.5] | 1 | 1 | 1 | 0.753 | 0.604 | 1.000 | 0.810 |
| 10 | batch_orchestrator_v1 | openai_gpt5.4_mini | openai-gpt-5.4-mini [OpenAI GPT-5.4 Mini] | 1 | 1 | 1 | 0.648 | 0.479 | 1.000 | 0.750 |
| 11 | batch_orchestrator_v1 | nvidia_nemotron_3_super_120b_a12b | nvidia-nemotron-3-super-120b-a12b [NVIDIA Nemotron 3 Super 120B A12B] | 3 | 2 | 3 | 0.265 | 0.172 | 0.655 | 0.534 |

### Review Rows

| Review | Suite | Studies | Architecture | Preset | Gatekeeper Model | Runs | Scored | F1 | Recall | Precision | Accuracy |
|--------|-------|---------|--------------|--------|------------------|------|--------|----|--------|-----------|----------|
| continuity_of_care_cancer_92 | screening_ladder_dev_no_label_0_5_v2 | 92 | batch_orchestrator_v1 | deepseek_v4_pro--xhigh | deepseek-v4-pro--xhigh [DeepSeek V4 Pro] | 1 | 1 | 0.811 | 0.714 | 0.938 | 0.848 |
| continuity_of_care_cancer_92 | screening_ladder_dev_no_label_0_5_v2 | 92 | batch_orchestrator_v1 | openai_gpt5--xhigh | openai-gpt-5--xhigh [OpenAI GPT5] | 1 | 1 | 0.778 | 0.667 | 0.933 | 0.826 |
| continuity_of_care_cancer_92 | screening_ladder_dev_no_label_0_5_v2 | 92 | batch_orchestrator_v1 | kimi_k2.6 | kimi-k2.6 [Kimi K2.6] | 1 | 1 | 0.557 | 0.405 | 0.895 | 0.707 |
| ovarian_cancer_diagnosis_92 | screening_ladder_dev_no_label_0_5 | 92 | batch_orchestrator_v1 | kimi_k2.6 | kimi-k2.6 [Kimi K2.6] | 1 | 1 | 0.926 | 0.978 | 0.880 | 0.924 |
| ovarian_cancer_diagnosis_92 | screening_ladder_dev_no_label_0_5 | 92 | batch_orchestrator_v1 | qwen3.5_122b_a10b | qwen3.5-122b-a10b [Qwen 3.5 122B A10B] | 1 | 1 | 0.907 | 0.978 | 0.846 | 0.902 |
| ovarian_cancer_diagnosis_92 | screening_ladder_dev_no_label_0_5 | 92 | batch_orchestrator_v1 | qwen3.5_27b | qwen3.5-27b [Qwen 3.5 27B] | 1 | 1 | 0.907 | 0.978 | 0.846 | 0.902 |
| ovarian_cancer_diagnosis_92 | screening_ladder_dev_no_label_0_5 | 92 | batch_orchestrator_v1 | openai_gpt_oss_120b | gpt-oss-120b [OpenAI GPT-OSS 120B] | 1 | 1 | 0.905 | 0.956 | 0.860 | 0.902 |
| ovarian_cancer_diagnosis_92 | screening_ladder_dev_no_label_0_5 | 92 | batch_orchestrator_v1 | deepseek_v4_pro--xhigh | deepseek-v4-pro--xhigh [DeepSeek V4 Pro] | 1 | 1 | 0.882 | 0.911 | 0.854 | 0.880 |
| ovarian_cancer_diagnosis_92 | screening_ladder_dev_no_label_0_5 | 92 | batch_orchestrator_v1 | openai_gpt5--xhigh | openai-gpt-5--xhigh [OpenAI GPT5] | 1 | 1 | 0.857 | 0.867 | 0.848 | 0.859 |
| ovarian_cancer_diagnosis_92 | screening_ladder_dev_no_label_0_5 | 92 | batch_orchestrator_v1 | nvidia_nemotron_3_super_120b_a12b | nvidia-nemotron-3-super-120b-a12b [NVIDIA Nemotron 3 Super 120B A12B] | 1 | 1 | 0.250 | 0.178 | 0.421 | 0.478 |
| desmopressin_transfusion_100 | screening_ladder_dev_exclude_balanced | 100 | batch_orchestrator_v1 | openai_gpt_oss_120b | gpt-oss-120b [OpenAI GPT-OSS 120B] | 1 | 1 | 0.949 | 0.903 | 1.000 | 0.930 |
| desmopressin_transfusion_100 | screening_ladder_dev_exclude_balanced | 100 | batch_orchestrator_v1 | qwen3.5_122b_a10b | qwen3.5-122b-a10b [Qwen 3.5 122B A10B] | 1 | 1 | 0.941 | 0.889 | 1.000 | 0.920 |
| desmopressin_transfusion_100 | screening_ladder_dev_exclude_balanced | 100 | batch_orchestrator_v1 | openai_gpt5 | openai-gpt-5 [OpenAI GPT5] | 1 | 1 | 0.884 | 0.792 | 1.000 | 0.850 |
| desmopressin_transfusion_100 | screening_ladder_dev_exclude_balanced | 100 | batch_orchestrator_v1 | qwen3.5_27b | qwen3.5-27b [Qwen 3.5 27B] | 1 | 1 | 0.875 | 0.778 | 1.000 | 0.840 |
| desmopressin_transfusion_100 | screening_ladder_dev_exclude_balanced | 100 | batch_orchestrator_v1 | kimi_k2.6 | kimi-k2.6 [Kimi K2.6] | 1 | 1 | 0.875 | 0.778 | 1.000 | 0.840 |
| desmopressin_transfusion_100 | screening_ladder_dev_exclude_balanced | 100 | batch_orchestrator_v1 | deepseek_v4_pro--xhigh | deepseek-v4-pro--xhigh [DeepSeek V4 Pro] | 1 | 1 | 0.866 | 0.764 | 1.000 | 0.830 |
| desmopressin_transfusion_100 | screening_ladder_dev_exclude_balanced | 100 | batch_orchestrator_v1 | openai_gpt5--xhigh | openai-gpt-5--xhigh [OpenAI GPT5] | 1 | 1 | 0.866 | 0.764 | 1.000 | 0.830 |
| desmopressin_transfusion_100 | screening_ladder_dev_exclude_balanced | 100 | batch_orchestrator_v1 | deepseek_v4_pro | deepseek-v4-pro [DeepSeek V4 Pro] | 1 | 1 | 0.857 | 0.750 | 1.000 | 0.820 |
| desmopressin_transfusion_100 | screening_ladder_dev_exclude_balanced | 100 | batch_orchestrator_v1 | nvidia_nemotron_3_super_120b_a12b | nvidia-nemotron-3-super-120b-a12b [NVIDIA Nemotron 3 Super 120B A12B] | 1 | 0 | n/a | n/a | n/a | n/a |
| pelvic_floor_training_100 | screening_ladder | 100 | batch_orchestrator_v1 | qwen3.5_122b_a10b | qwen3.5-122b-a10b [Qwen 3.5 122B A10B] | 1 | 1 | 0.833 | 0.729 | 0.972 | 0.860 |
| pelvic_floor_training_100 | screening_ladder | 100 | batch_orchestrator_v1 | deepseek_v4_pro | deepseek-v4-pro [DeepSeek V4 Pro] | 1 | 1 | 0.829 | 0.708 | 1.000 | 0.860 |
| pelvic_floor_training_100 | screening_ladder | 100 | batch_orchestrator_v1 | kimi_k2.6 | kimi-k2.6 [Kimi K2.6] | 1 | 1 | 0.815 | 0.688 | 1.000 | 0.850 |
| pelvic_floor_training_100 | screening_ladder | 100 | batch_orchestrator_v1 | openai_gpt5 | openai-gpt-5 [OpenAI GPT5] | 1 | 1 | 0.800 | 0.667 | 1.000 | 0.840 |
| pelvic_floor_training_100 | screening_ladder | 100 | batch_orchestrator_v1 | deepseek_v4_pro--xhigh | deepseek-v4-pro--xhigh [DeepSeek V4 Pro] | 1 | 1 | 0.800 | 0.667 | 1.000 | 0.840 |
| pelvic_floor_training_100 | screening_ladder | 100 | batch_orchestrator_v1 | openai_gpt5--xhigh | openai-gpt-5--xhigh [OpenAI GPT5] | 1 | 1 | 0.785 | 0.646 | 1.000 | 0.830 |
| pelvic_floor_training_100 | screening_ladder | 100 | batch_orchestrator_v1 | mistral_medium_3.5 | mistral-medium-3.5 [Mistral Medium 3.5] | 1 | 1 | 0.753 | 0.604 | 1.000 | 0.810 |
| pelvic_floor_training_100 | screening_ladder | 100 | batch_orchestrator_v1 | qwen3.5_27b | qwen3.5-27b [Qwen 3.5 27B] | 1 | 1 | 0.720 | 0.562 | 1.000 | 0.790 |
| pelvic_floor_training_100 | screening_ladder | 100 | batch_orchestrator_v1 | openai_gpt5.4_mini | openai-gpt-5.4-mini [OpenAI GPT-5.4 Mini] | 1 | 1 | 0.648 | 0.479 | 1.000 | 0.750 |
| pelvic_floor_training_100 | screening_ladder | 100 | batch_orchestrator_v1 | openai_gpt_oss_120b | gpt-oss-120b [OpenAI GPT-OSS 120B] | 1 | 1 | 0.648 | 0.479 | 1.000 | 0.750 |
| pelvic_floor_training_100 | screening_ladder | 100 | batch_orchestrator_v1 | nvidia_nemotron_3_super_120b_a12b | nvidia-nemotron-3-super-120b-a12b [NVIDIA Nemotron 3 Super 120B A12B] | 1 | 1 | 0.281 | 0.167 | 0.889 | 0.590 |

## large_100_plus (100+)

### Model Averages

| Rank | Architecture | Preset | Gatekeeper Model | Runs | Scored | Reviews | F1 | Recall | Precision | Accuracy |
|------|--------------|--------|------------------|------|--------|---------|----|--------|-----------|----------|
| 1 | batch_orchestrator_v1 | deepseek_v4_pro--xhigh | deepseek-v4-pro--xhigh [DeepSeek V4 Pro] | 4 | 4 | 4 | 0.714 | 0.657 | 0.980 | 0.745 |
| 2 | batch_orchestrator_v1 | qwen3.5_122b_a10b | qwen3.5-122b-a10b [Qwen 3.5 122B A10B] | 3 | 3 | 3 | 0.688 | 0.610 | 0.983 | 0.714 |
| 3 | batch_orchestrator_v1 | qwen3.5_27b | qwen3.5-27b [Qwen 3.5 27B] | 3 | 3 | 3 | 0.677 | 0.641 | 0.885 | 0.654 |
| 4 | batch_orchestrator_v1 | openai_gpt5--xhigh | openai-gpt-5--xhigh [OpenAI GPT5] | 4 | 4 | 4 | 0.659 | 0.583 | 0.984 | 0.692 |
| 5 | batch_orchestrator_v1 | kimi_k2.6 | kimi-k2.6 [Kimi K2.6] | 4 | 4 | 4 | 0.598 | 0.519 | 0.980 | 0.644 |
| 6 | batch_orchestrator_v1 | openai_gpt_oss_120b | gpt-oss-120b [OpenAI GPT-OSS 120B] | 3 | 3 | 3 | 0.525 | 0.523 | 0.839 | 0.542 |
| 7 | batch_orchestrator_v1 | openai_gpt5.4_mini | openai-gpt-5.4-mini [OpenAI GPT-5.4 Mini] | 1 | 1 | 1 | 0.492 | 0.336 | 0.920 | 0.525 |
| 8 | batch_orchestrator_v1 | openai_gpt5 | openai-gpt-5 [OpenAI GPT5] | 2 | 2 | 2 | 0.461 | 0.374 | 0.981 | 0.549 |
| 9 | batch_orchestrator_v1 | deepseek_v4_pro | deepseek-v4-pro [DeepSeek V4 Pro] | 2 | 2 | 2 | 0.437 | 0.369 | 0.982 | 0.546 |
| 10 | batch_orchestrator_v1 | nvidia_nemotron_3_super_120b_a12b | nvidia-nemotron-3-super-120b-a12b [NVIDIA Nemotron 3 Super 120B A12B] | 3 | 2 | 3 | 0.389 | 0.276 | 0.936 | 0.475 |
| 11 | batch_orchestrator_v1 | mistral_medium_3.5 | mistral-medium-3.5 [Mistral Medium 3.5] | 1 | 1 | 1 | 0.185 | 0.102 | 1.000 | 0.385 |

### Review Rows

| Review | Suite | Studies | Architecture | Preset | Gatekeeper Model | Runs | Scored | F1 | Recall | Precision | Accuracy |
|--------|-------|---------|--------------|--------|------------------|------|--------|----|--------|-----------|----------|
| glaucoma_140 | screening_ladder_dev_no_label_0_5_v2 | 140 | batch_orchestrator_v1 | openai_gpt5--xhigh | openai-gpt-5--xhigh [OpenAI GPT5] | 1 | 1 | 0.990 | 1.000 | 0.980 | 0.986 |
| glaucoma_140 | screening_ladder_dev_no_label_0_5_v2 | 140 | batch_orchestrator_v1 | kimi_k2.6 | kimi-k2.6 [Kimi K2.6] | 1 | 1 | 0.979 | 0.979 | 0.979 | 0.971 |
| glaucoma_140 | screening_ladder_dev_no_label_0_5_v2 | 140 | batch_orchestrator_v1 | deepseek_v4_pro--xhigh | deepseek-v4-pro--xhigh [DeepSeek V4 Pro] | 1 | 1 | 0.974 | 0.990 | 0.960 | 0.964 |
| home_based_rehabilitation_183 | screening_ladder_dev_no_label_0_5 | 183 | batch_orchestrator_v1 | qwen3.5_122b_a10b | qwen3.5-122b-a10b [Qwen 3.5 122B A10B] | 1 | 1 | 0.955 | 0.928 | 0.985 | 0.934 |
| home_based_rehabilitation_183 | screening_ladder_dev_no_label_0_5 | 183 | batch_orchestrator_v1 | deepseek_v4_pro--xhigh | deepseek-v4-pro--xhigh [DeepSeek V4 Pro] | 1 | 1 | 0.930 | 0.870 | 1.000 | 0.902 |
| home_based_rehabilitation_183 | screening_ladder_dev_no_label_0_5 | 183 | batch_orchestrator_v1 | openai_gpt_oss_120b | gpt-oss-120b [OpenAI GPT-OSS 120B] | 1 | 1 | 0.869 | 0.964 | 0.792 | 0.781 |
| home_based_rehabilitation_183 | screening_ladder_dev_no_label_0_5 | 183 | batch_orchestrator_v1 | qwen3.5_27b | qwen3.5-27b [Qwen 3.5 27B] | 1 | 1 | 0.860 | 1.000 | 0.754 | 0.754 |
| home_based_rehabilitation_183 | screening_ladder_dev_no_label_0_5 | 183 | batch_orchestrator_v1 | kimi_k2.6 | kimi-k2.6 [Kimi K2.6] | 1 | 1 | 0.802 | 0.674 | 0.989 | 0.749 |
| home_based_rehabilitation_183 | screening_ladder_dev_no_label_0_5 | 183 | batch_orchestrator_v1 | openai_gpt5--xhigh | openai-gpt-5--xhigh [OpenAI GPT5] | 1 | 1 | 0.800 | 0.667 | 1.000 | 0.749 |
| home_based_rehabilitation_183 | screening_ladder_dev_no_label_0_5 | 183 | batch_orchestrator_v1 | nvidia_nemotron_3_super_120b_a12b | nvidia-nemotron-3-super-120b-a12b [NVIDIA Nemotron 3 Super 120B A12B] | 1 | 1 | 0.631 | 0.471 | 0.956 | 0.585 |
| prom_feedback_194 | screening_ladder_dev_exclude_balanced | 194 | batch_orchestrator_v1 | qwen3.5_122b_a10b | qwen3.5-122b-a10b [Qwen 3.5 122B A10B] | 1 | 1 | 0.844 | 0.750 | 0.965 | 0.789 |
| prom_feedback_194 | screening_ladder_dev_exclude_balanced | 194 | batch_orchestrator_v1 | deepseek_v4_pro | deepseek-v4-pro [DeepSeek V4 Pro] | 1 | 1 | 0.817 | 0.709 | 0.963 | 0.758 |
| prom_feedback_194 | screening_ladder_dev_exclude_balanced | 194 | batch_orchestrator_v1 | qwen3.5_27b | qwen3.5-27b [Qwen 3.5 27B] | 1 | 1 | 0.808 | 0.696 | 0.963 | 0.747 |
| prom_feedback_194 | screening_ladder_dev_exclude_balanced | 194 | batch_orchestrator_v1 | deepseek_v4_pro--xhigh | deepseek-v4-pro--xhigh [DeepSeek V4 Pro] | 1 | 1 | 0.803 | 0.689 | 0.962 | 0.742 |
| prom_feedback_194 | screening_ladder_dev_exclude_balanced | 194 | batch_orchestrator_v1 | openai_gpt5 | openai-gpt-5 [OpenAI GPT5] | 1 | 1 | 0.798 | 0.682 | 0.962 | 0.737 |
| prom_feedback_194 | screening_ladder_dev_exclude_balanced | 194 | batch_orchestrator_v1 | openai_gpt5--xhigh | openai-gpt-5--xhigh [OpenAI GPT5] | 1 | 1 | 0.749 | 0.615 | 0.958 | 0.686 |
| prom_feedback_194 | screening_ladder_dev_exclude_balanced | 194 | batch_orchestrator_v1 | openai_gpt_oss_120b | gpt-oss-120b [OpenAI GPT-OSS 120B] | 1 | 1 | 0.636 | 0.568 | 0.724 | 0.505 |
| prom_feedback_194 | screening_ladder_dev_exclude_balanced | 194 | batch_orchestrator_v1 | kimi_k2.6 | kimi-k2.6 [Kimi K2.6] | 1 | 1 | 0.555 | 0.392 | 0.951 | 0.521 |
| prom_feedback_194 | screening_ladder_dev_exclude_balanced | 194 | batch_orchestrator_v1 | nvidia_nemotron_3_super_120b_a12b | nvidia-nemotron-3-super-120b-a12b [NVIDIA Nemotron 3 Super 120B A12B] | 1 | 0 | n/a | n/a | n/a | n/a |
| heart_failure_mhealth_200 | screening_ladder | 200 | batch_orchestrator_v1 | openai_gpt5.4_mini | openai-gpt-5.4-mini [OpenAI GPT-5.4 Mini] | 1 | 1 | 0.492 | 0.336 | 0.920 | 0.525 |
| heart_failure_mhealth_200 | screening_ladder | 200 | batch_orchestrator_v1 | qwen3.5_27b | qwen3.5-27b [Qwen 3.5 27B] | 1 | 1 | 0.365 | 0.226 | 0.939 | 0.460 |
| heart_failure_mhealth_200 | screening_ladder | 200 | batch_orchestrator_v1 | qwen3.5_122b_a10b | qwen3.5-122b-a10b [Qwen 3.5 122B A10B] | 1 | 1 | 0.266 | 0.153 | 1.000 | 0.420 |
| heart_failure_mhealth_200 | screening_ladder | 200 | batch_orchestrator_v1 | mistral_medium_3.5 | mistral-medium-3.5 [Mistral Medium 3.5] | 1 | 1 | 0.185 | 0.102 | 1.000 | 0.385 |
| heart_failure_mhealth_200 | screening_ladder | 200 | batch_orchestrator_v1 | deepseek_v4_pro--xhigh | deepseek-v4-pro--xhigh [DeepSeek V4 Pro] | 1 | 1 | 0.149 | 0.080 | 1.000 | 0.370 |
| heart_failure_mhealth_200 | screening_ladder | 200 | batch_orchestrator_v1 | nvidia_nemotron_3_super_120b_a12b | nvidia-nemotron-3-super-120b-a12b [NVIDIA Nemotron 3 Super 120B A12B] | 1 | 1 | 0.148 | 0.080 | 0.917 | 0.365 |
| heart_failure_mhealth_200 | screening_ladder | 200 | batch_orchestrator_v1 | openai_gpt5 | openai-gpt-5 [OpenAI GPT5] | 1 | 1 | 0.123 | 0.066 | 1.000 | 0.360 |
| heart_failure_mhealth_200 | screening_ladder | 200 | batch_orchestrator_v1 | openai_gpt5--xhigh | openai-gpt-5--xhigh [OpenAI GPT5] | 1 | 1 | 0.097 | 0.051 | 1.000 | 0.350 |
| heart_failure_mhealth_200 | screening_ladder | 200 | batch_orchestrator_v1 | openai_gpt_oss_120b | gpt-oss-120b [OpenAI GPT-OSS 120B] | 1 | 1 | 0.070 | 0.036 | 1.000 | 0.340 |
| heart_failure_mhealth_200 | screening_ladder | 200 | batch_orchestrator_v1 | deepseek_v4_pro | deepseek-v4-pro [DeepSeek V4 Pro] | 1 | 1 | 0.057 | 0.029 | 1.000 | 0.335 |
| heart_failure_mhealth_200 | screening_ladder | 200 | batch_orchestrator_v1 | kimi_k2.6 | kimi-k2.6 [Kimi K2.6] | 1 | 1 | 0.057 | 0.029 | 1.000 | 0.335 |

