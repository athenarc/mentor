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
