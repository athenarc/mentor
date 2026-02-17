"""
Bastirr configuration and environment management.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
DATASET_DIR = PROJECT_ROOT / "systematic_review_dataset" / "20240827_Systematic_Review_Data"
BASTIRR_DIR = PROJECT_ROOT / "bastirr"
OUTPUT_DIR = BASTIRR_DIR / "output"

# ---------------------------------------------------------------------------
# Agent execution settings
# ---------------------------------------------------------------------------
# Per-step code execution timeout in seconds.
# smolagents defaults to 30s which is too short for LLM tool calls that
# process many studies.  ``None`` disables the timeout entirely; prefer a
# generous finite value so genuine infinite loops still get caught.
EXECUTOR_TIMEOUT_SECONDS = int(os.getenv("BASTIRR_EXECUTOR_TIMEOUT", "300"))

# ---------------------------------------------------------------------------
# API keys  (sourced from .env)
# ---------------------------------------------------------------------------
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# ---------------------------------------------------------------------------
# Model configuration
# ---------------------------------------------------------------------------
# Model backend: "openai" for OpenAIServerModel, "litellm" for LiteLLMModel
MODEL_BACKEND = os.getenv("BASTIRR_MODEL_BACKEND", "openai")

# Model identifier  (provider-prefixed for LiteLLM, e.g. "ollama_chat/llama3")
DEFAULT_MODEL_ID = os.getenv("BASTIRR_MODEL", "gpt-4o")

# Optional: API base URL (for local servers such as Ollama, vLLM, etc.)
API_BASE = os.getenv("BASTIRR_API_BASE", "")  # e.g. http://localhost:11434

# Optional: generic API key (used by LiteLLM when OPENAI_API_KEY is not appropriate)
API_KEY = os.getenv("BASTIRR_API_KEY", "")

# ---------------------------------------------------------------------------
# Dataset files
# ---------------------------------------------------------------------------
DATASET_FILES = {
    "dev": DATASET_DIR / "20240827_dev_set.csv",
    "val": DATASET_DIR / "20240827_val_set.csv",
    "random_test": DATASET_DIR / "20240827_random_test_set.csv",
    "heart_test": DATASET_DIR / "20240827_heart_test_set.csv",
    "HIV_test": DATASET_DIR / "20240827_HIV_test_set.csv",
}

# ---------------------------------------------------------------------------
# Column mapping for the Cochrane dataset
# ---------------------------------------------------------------------------
DATASET_COLUMNS = {
    "review_url": "Review_URL",
    "review_title": "Review_Title",
    "background": "Background",
    "objective": "Objective",
    "selection_criteria": "Selection_criteria",
    "study_title": "Title",
    "abstract": "Abstract_clean",
    "label": "label",
}

# Label semantics: 1.0 = included, 0.5 = excluded after full-text, 0.0 = excluded at screening
LABEL_INCLUDED = 1.0
LABEL_EXCLUDED_FULLTEXT = 0.5
LABEL_EXCLUDED_SCREENING = 0.0


# ---------------------------------------------------------------------------
# Model factory
# ---------------------------------------------------------------------------

def create_model(
    model_id: str | None = None,
    backend: str | None = None,
    api_key: str | None = None,
    api_base: str | None = None,
    **kwargs,
):
    """
    Create a smolagents model instance based on configuration.

    Args:
        model_id: Model identifier. Defaults to ``BASTIRR_MODEL`` env var / ``gpt-4o``.
            For LiteLLM, use provider-prefixed IDs like ``anthropic/claude-3-5-sonnet-latest``
            or ``ollama_chat/llama3.2``.
        backend: ``"openai"`` or ``"litellm"``. Defaults to ``BASTIRR_MODEL_BACKEND`` env var.
        api_key: API key override. Defaults to ``BASTIRR_API_KEY`` or ``OPENAI_API_KEY``.
        api_base: API base URL override (for local servers). Defaults to ``BASTIRR_API_BASE``.
        **kwargs: Extra keyword arguments forwarded to the model constructor
            (e.g. ``temperature``, ``num_ctx``).

    Returns:
        A smolagents ``Model`` instance (``OpenAIServerModel`` or ``LiteLLMModel``).
    """
    _backend = (backend or MODEL_BACKEND).lower()
    _model_id = model_id or DEFAULT_MODEL_ID
    _api_key = api_key or API_KEY or OPENAI_API_KEY
    _api_base = api_base or API_BASE or None

    if _backend == "litellm":
        from smolagents import LiteLLMModel

        litellm_kwargs = {"model_id": _model_id}
        if _api_key:
            litellm_kwargs["api_key"] = _api_key
        if _api_base:
            litellm_kwargs["api_base"] = _api_base
        litellm_kwargs.update(kwargs)
        return LiteLLMModel(**litellm_kwargs)

    if _backend == "hf-hub":
        from smolagents import TransformersModel

        hfh_kwargs = {"model_id": _model_id}
        hfh_kwargs.update(kwargs)
        return TransformersModel(**hfh_kwargs)

    # Default: OpenAI
    from smolagents import OpenAIServerModel

    openai_kwargs: dict = {"model_id": _model_id}
    if _api_key:
        openai_kwargs["api_key"] = _api_key
    if _api_base:
        openai_kwargs["api_base"] = _api_base
    openai_kwargs.update(kwargs)
    return OpenAIServerModel(**openai_kwargs)
