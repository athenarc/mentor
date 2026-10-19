"""Display labels and filter mappings for the benchmark Streamlit UI.

Maps human-readable architecture, gold-label policy, and model names to the
values stored in harness ``summary.json`` files, plus logging level indices
and deployment-tier groupings for research-question views.
"""

import logging

LOGGING_LEVEL = [
    logging.CRITICAL + 1,
    logging.WARNING,
    logging.INFO,
    logging.DEBUG
]

GOLD_LABEL_POLICY_LABEL_TO_VALUE_INDEX = {
    'exclude': 'exclude_label_0_5',
    'include': 'include_label_0_5'
}

GOLD_LABEL_POLICY_VALUE_TO_LABEL_INDEX = {v: k for k, v in GOLD_LABEL_POLICY_LABEL_TO_VALUE_INDEX.items()}

EXPERIMENT_ARCHITECTURE_LABEL_TO_VALUE_INDEX = {
    'bulk': 'batch_orchestrator_v1',
    'batch': 'loop_chunk_orchestrator_v1',
    'one_by_one': 'loop_orchestrator_v1'
}

EXPERIMENT_ARCHITECTURE_VALUE_TO_LABEL_INDEX = {v: k for k, v in EXPERIMENT_ARCHITECTURE_LABEL_TO_VALUE_INDEX.items()}

MODEL_LABEL_TO_VALUE_INDEX = {
    'kimi_k2.6': 'kimi_k2.6',
    'deepseek_v4_pro--xhigh': 'deepseek_v4_pro--xhigh',
    'openai_gpt5': 'openai_gpt5',
    'qwen3.5_27b': 'qwen3.5_27b',
    'deepseek_v4_pro': 'deepseek_v4_pro',
    'openai_gpt5.4_mini': 'openai_gpt5.4_mini',
    'openai_gpt5--xhigh': 'openai_gpt5--xhigh',
    'qwen3.5_122b_a10b': 'qwen3.5_122b_a10b',
    'mistral_medium_3.5': 'mistral_medium_3.5',
    'openai_gpt_oss_120b': 'openai_gpt_oss_120b',
    'nvidia_nemotron_3_super_120b_a12b': 'nvidia_nemotron_3_super_120b_a12b'
}

MODEL_DEPLOYMENT_TIERS = {
    'locally_deployable': {
        'qwen3.5_27b',
        'qwen3.5_122b_a10b',
        'mistral_medium_3.5',
        'nvidia_nemotron_3_super_120b_a12b',
        'openai_gpt_oss_120b'
    },
    'provided': {
        'kimi_k2.6',
        'deepseek_v4_pro--xhigh',
        'deepseek_v4_pro',
        'openai_gpt5',
        'openai_gpt5--xhigh',
        'openai_gpt5.4_mini'
    }
}

# class LoggingLevel(enum.IntEnum):
#     DEBUG = 3
#     INFO = 2
#     WARNING = 1
#     SILENT = 0
#
#     def to_internal_value(self) -> int:
#         return {
#             LoggingLevel.DEBUG: logging.DEBUG,
#             LoggingLevel.INFO: logging.INFO,
#             LoggingLevel.WARNING: logging.WARNING,
#             LoggingLevel.SILENT: logging.CRITICAL + 1,
#         }[self]
#
#     def __str__(self):
#         return str(self.value)
#
#
# class GoldLabelPolicy(enum.Enum):
#     EXCLUDE = 'exclude'
#     INCLUDE = 'include'
#
#     def __str__(self):
#         return str(self.value)
#
# GOLD_LABEL_POLICY_LABEL_TO_VALUE_INDEX = {
#     GoldLabelPolicy.EXCLUDE.value: 'exclude_label_0_5',
#     GoldLabelPolicy.INCLUDE.value: 'include_label_0_5',
# }
#
# class ExperimentArchitecture(enum.Enum):
#     BULK = 'bulk'
#     BATCH = 'batch'
#     ONE_BY_ONE = 'one_by_one'
#
#     def __str__(self):
#         return str(self.value)
#
# EXPERIMENT_ARCHITECTURE_LABEL_TO_VALUE_INDEX = {
#     ExperimentArchitecture.BULK.value: 'batch_orchestrator_v1',
#     ExperimentArchitecture.BATCH.value: 'loop_chunk_orchestrator_v1',
#     ExperimentArchitecture.ONE_BY_ONE.value: 'loop_orchestrator_v1',
# }
#
#
# class Model(enum.Enum):
#     KIMI_K2_6 = 'kimi_k2.6'
#     DEEPSEEK_V4_PRO__XHIGH = 'deepseek_v4_pro--xhigh'
#     OPENAI_GPT5 = 'openai_gpt5'
#     QWEN3_5_27B = 'qwen3.5_27b'
#     DEEPSEEK_V4_PRO = 'deepseek_v4_pro'
#     OPENAI_GPT5_4_MINI = 'openai_gpt5.4_mini'
#     OPENAI_GPT5__XHIGH = 'openai_gpt5--xhigh'
#     QWEN3_5_122B_A10B = 'qwen3.5_122b_a10b'
#     MISTRAL_MEDIUM_3_5 = 'mistral_medium_3.5'
#     OPENAI_GPT_OSS_120B = 'openai_gpt_oss_120b'
#     NVIDIA_NEMOTRON_3_SUPER_120B_A12B = 'nvidia_nemotron_3_super_120b_a12b'
#
#     def __str__(self):
#         return str(self.value)
