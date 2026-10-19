"""
smolagents model factory and env resolution helpers.

Used by ``prepare_run_session`` and ``profile_resolver`` when building
role-specific or shared LLM clients.
"""

from __future__ import annotations

import os

from mentor.settings import (
    API_BASE,
    DEFAULT_MODEL_ID,
    MODEL_BACKEND,
    OPENAI_API_KEY,
)


def resolve_backend(backend: str | None = None) -> str:
    """Resolve the effective model backend."""
    return (backend or os.getenv("MENTOR_MODEL_BACKEND", MODEL_BACKEND)).lower()


def resolve_model_id(model_id: str | None = None) -> str:
    """Resolve the effective model identifier."""
    return model_id or os.getenv("MENTOR_MODEL", DEFAULT_MODEL_ID)


def resolve_api_key(api_key: str | None = None) -> str:
    """Resolve the effective API key for OpenAI-compatible backends."""
    return (
        api_key
        or os.getenv("MENTOR_API_KEY", "").strip()
        or os.getenv("OPENAI_API_KEY", OPENAI_API_KEY).strip()
    )


def resolve_api_base(api_base: str | None = None) -> str | None:
    """Resolve the effective API base URL."""
    return api_base or os.getenv("MENTOR_API_BASE", API_BASE).strip() or None


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
        model_id: Model identifier. Defaults to ``MENTOR_MODEL`` / ``gpt-5``.
            For LiteLLM, use provider-prefixed IDs like ``ollama_chat/llama3.2``.
        backend: ``"openai"``, ``"litellm"``, or ``"hf-hub"``.
        api_key: API key override. Defaults to ``MENTOR_API_KEY`` or ``OPENAI_API_KEY``.
        api_base: API base URL override. Defaults to ``MENTOR_API_BASE``.
        **kwargs: Extra keyword arguments forwarded to the model constructor.

    Returns:
        A smolagents ``Model`` instance.
    """
    _backend = resolve_backend(backend)
    _model_id = resolve_model_id(model_id)
    _api_key = resolve_api_key(api_key)
    _api_base = resolve_api_base(api_base)

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

        return TransformersModel(model_id=_model_id, **kwargs)

    from smolagents import OpenAIServerModel

    openai_kwargs: dict = {"model_id": _model_id}
    if _api_key:
        openai_kwargs["api_key"] = _api_key
    if _api_base:
        openai_kwargs["api_base"] = _api_base
    openai_kwargs.update(kwargs)
    return OpenAIServerModel(**openai_kwargs)
