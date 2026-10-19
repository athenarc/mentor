"""
Gatekeeper (and fixed orchestrator) model presets for benchmarks.

Presets live in ``experiments/config/models.json``; ``resolve_model_presets``
expands CLI ``--model-presets all`` into concrete ``ResolvedModelPreset``
entries with env-backed API keys isolated from production ``mentor`` profiles.
"""

from __future__ import annotations

import json
import os
from typing import Any
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from smolagents import LiteLLMModel, OpenAIServerModel, TransformersModel

from mentor.config import MODEL_REQUEST_TIMEOUT_SECONDS


_CONFIG_DIR = Path(__file__).resolve().parents[1] / "config"
_DEFAULT_CONFIG_PATH = _CONFIG_DIR / "models.json"


@dataclass(frozen=True)
class ResolvedModelPreset:
    """Fully resolved model configuration for one benchmark run."""

    key: str
    description: str
    display_name: str
    backend: str
    model_id: str
    api_base: str | None
    api_key: str | None
    api_key_source: str
    request_kwargs: dict[str, Any] | None = None
    default_api_key: str | None = None

    def create_model(self):
        """Instantiate the smolagents model for this preset without env leakage."""
        api_key = self.api_key or self.default_api_key
        request_kwargs = dict(self.request_kwargs or {})
        request_timeout = MODEL_REQUEST_TIMEOUT_SECONDS

        if self.backend == "litellm":
            kwargs = {"model_id": self.model_id}
            if api_key:
                kwargs["api_key"] = api_key
            if self.api_base:
                kwargs["api_base"] = self.api_base
            if request_timeout:
                kwargs.setdefault("timeout", request_timeout)
            kwargs.update(request_kwargs)
            return LiteLLMModel(**kwargs)

        if self.backend == "hf-hub":
            return TransformersModel(model_id=self.model_id)

        client_kwargs = {}
        if request_timeout:
            client_kwargs["timeout"] = request_timeout
        kwargs = {"model_id": self.model_id, "client_kwargs": client_kwargs}
        if api_key:
            kwargs["api_key"] = api_key
        if self.api_base:
            kwargs["api_base"] = self.api_base
        kwargs.update(request_kwargs)
        return OpenAIServerModel(**kwargs)

    @property
    def model_label(self) -> str:
        """Human-facing label used in persisted benchmark artifacts."""
        if self.description:
            return f"{self.display_name} [{self.description}]"
        return self.display_name

    def metadata(self) -> dict[str, str]:
        """Return serializable metadata for summaries and metrics."""
        return {
            "preset": self.key,
            "display_name": self.display_name,
            "model_label": self.model_label,
            "backend": self.backend,
            "model_id": self.model_id,
            "api_base": self.api_base or "",
            "api_key_source": self.api_key_source,
        }


@dataclass(frozen=True)
class ModelPreset:
    """Model preset template with config-backed defaults and env overrides."""

    key: str
    description: str
    display_name_default: str
    backend: str
    model_id_default: str
    api_base_default: str | None = None
    api_key_env_var: str | None = None
    requires_api_key: bool = False
    default_api_key: str | None = None
    display_name_env_var: str | None = None
    model_id_env_var: str | None = None
    api_base_env_var: str | None = None
    request_kwargs_default: dict[str, Any] | None = None

    def resolve(self, *, strict: bool = True) -> ResolvedModelPreset:
        """Resolve config-backed and environment-backed details."""
        display_name = (
            os.getenv(self.display_name_env_var, "").strip()
            if self.display_name_env_var
            else ""
        ) or self.display_name_default
        model_id = (
            os.getenv(self.model_id_env_var, "").strip()
            if self.model_id_env_var
            else ""
        ) or self.model_id_default
        api_base = (
            os.getenv(self.api_base_env_var, "").strip()
            if self.api_base_env_var
            else ""
        ) or self.api_base_default

        api_key = self.default_api_key
        api_key_source = "not_required"
        if self.api_key_env_var:
            api_key_source = self.api_key_env_var
            env_value = os.getenv(self.api_key_env_var, "").strip()
            if env_value:
                api_key = env_value

        if strict and self.requires_api_key and not api_key:
            raise ValueError(
                f"Model preset '{self.key}' requires {self.api_key_env_var} to be set."
            )

        return ResolvedModelPreset(
            key=self.key,
            description=self.description,
            display_name=display_name,
            backend=self.backend,
            model_id=model_id,
            api_base=api_base,
            api_key=api_key,
            api_key_source=api_key_source,
            request_kwargs=self.request_kwargs_default,
            default_api_key=self.default_api_key,
        )


@lru_cache(maxsize=1)
def _load_model_preset_config() -> dict:
    with open(_get_config_path(), "r", encoding="utf-8") as f:
        return json.load(f)


@lru_cache(maxsize=1)
def _get_config_path() -> Path:
    raw_path = os.getenv("MENTOR_MODEL_PRESETS_CONFIG", "").strip()
    if not raw_path:
        return _DEFAULT_CONFIG_PATH

    candidate = Path(raw_path)
    if not candidate.is_absolute():
        candidate = _CONFIG_DIR / candidate
    return candidate


@lru_cache(maxsize=1)
def _build_canonical_model_presets() -> dict[str, ModelPreset]:
    config = _load_model_preset_config()
    presets: dict[str, ModelPreset] = {}
    for item in config["canonical_presets"]:
        preset = ModelPreset(
            key=item["key"],
            description=item["description"],
            display_name_default=item["display_name_default"],
            backend=item["backend"],
            model_id_default=item["model_id_default"],
            api_base_default=item.get("api_base_default"),
            api_key_env_var=item.get("api_key_env_var"),
            requires_api_key=bool(item.get("requires_api_key", False)),
            default_api_key=item.get("default_api_key"),
            display_name_env_var=item.get("display_name_env_var"),
            model_id_env_var=item.get("model_id_env_var"),
            api_base_env_var=item.get("api_base_env_var"),
            request_kwargs_default=item.get("request_kwargs_default"),
        )
        presets[preset.key] = preset
    return presets


def list_model_presets() -> list[str]:
    """Return the available canonical benchmark model preset keys."""
    return sorted(_build_canonical_model_presets())


def get_model_preset(name: str) -> ModelPreset:
    """Return a canonical model preset."""
    presets = _build_canonical_model_presets()
    if name not in presets:
        raise ValueError(
            f"Unknown model preset '{name}'. Available presets: {', '.join(list_model_presets())}"
        )
    return presets[name]


def resolve_model_presets(names: list[str] | None = None) -> list[ResolvedModelPreset]:
    """
    Resolve one or more preset names into concrete model configurations.

    Args:
        names: Optional list of preset keys. ``None`` or ``['all']`` resolves
            every canonical preset in registry order.
    """
    if not names or "all" in names:
        ordered_names = list(_build_canonical_model_presets())
    else:
        ordered_names = names
    return [get_model_preset(name).resolve(strict=True) for name in ordered_names]


CANONICAL_MODEL_PRESETS = _build_canonical_model_presets()
