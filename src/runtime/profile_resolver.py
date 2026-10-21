"""
Resolve model connections and role→model profiles from ``mentor/config/model_profiles.json``.

``models`` is the catalogue of LLM connections. ``profiles`` map agent roles
to model keys (``shared`` fills any role without its own entry). A bare model
key is treated as ``{"shared": key}``.
"""

from __future__ import annotations

import copy
import json
import os
from dataclasses import dataclass, replace
from functools import lru_cache
from pathlib import Path
from typing import Any

from mentor.runtime.models import create_model
from mentor.settings import MODEL_REQUEST_TIMEOUT_SECONDS

MODEL_ROLES = ("orchestrator", "librarian", "gatekeeper", "miner", "critic")
_SUPPORTED_KEYS = frozenset(("shared", *MODEL_ROLES))
_DEFAULT_CONFIG_PATH = Path(__file__).resolve().parents[1] / "config" / "model_profiles.json"


def _as_env_names(value: str | list[str] | None) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    return [item for item in value if item]


def _first_env(names: list[str]) -> tuple[str | None, str | None]:
    for name in names:
        value = os.getenv(name, "").strip()
        if value:
            return value, name
    return None, None


def _env_or(item: dict[str, Any], key: str, env_key: str) -> str:
    """Prefer non-empty env var named in ``item[env_key]``, else ``item[key]``."""
    env_name = item.get(env_key)
    if env_name:
        override = os.getenv(env_name, "").strip()
        if override:
            return override
    value = item.get(key)
    if value is None:
        return ""
    return str(value)


@lru_cache(maxsize=1)
def _load_catalog() -> dict[str, Any]:
    raw = os.getenv("MENTOR_MODELS_CONFIG", "").strip()
    path = Path(raw) if raw else _DEFAULT_CONFIG_PATH
    if raw and not path.is_absolute():
        path = _DEFAULT_CONFIG_PATH.parent / path
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _clear_catalog_cache() -> None:
    _load_catalog.cache_clear()
    _model_registry.cache_clear()
    _profile_registry.cache_clear()


@lru_cache(maxsize=1)
def _model_registry() -> dict[str, dict[str, Any]]:
    return {item["key"]: item for item in _load_catalog().get("models", [])}


@lru_cache(maxsize=1)
def _profile_registry() -> dict[str, dict[str, Any]]:
    return {item["key"]: item for item in _load_catalog().get("profiles", [])}


@dataclass(frozen=True)
class ResolvedModel:
    """Fully resolved model connection (one catalogue entry)."""

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
        """Instantiate the smolagents model for this entry."""
        api_key = self.api_key or self.default_api_key
        request_kwargs = dict(self.request_kwargs or {})
        request_timeout = MODEL_REQUEST_TIMEOUT_SECONDS

        if self.backend == "litellm":
            kwargs: dict[str, Any] = {"model_id": self.model_id}
            if api_key:
                kwargs["api_key"] = api_key
            if self.api_base:
                kwargs["api_base"] = self.api_base
            if request_timeout:
                kwargs.setdefault("timeout", request_timeout)
            kwargs.update(request_kwargs)
            from smolagents import LiteLLMModel

            return LiteLLMModel(**kwargs)

        if self.backend == "hf-hub":
            from smolagents import TransformersModel

            return TransformersModel(model_id=self.model_id)

        client_kwargs: dict[str, Any] = {}
        if request_timeout:
            client_kwargs["timeout"] = request_timeout
        kwargs = {"model_id": self.model_id, "client_kwargs": client_kwargs}
        if api_key:
            kwargs["api_key"] = api_key
        if self.api_base:
            kwargs["api_base"] = self.api_base
        kwargs.update(request_kwargs)
        from smolagents import OpenAIServerModel

        return OpenAIServerModel(**kwargs)

    @property
    def model_label(self) -> str:
        """Human-facing label used in persisted artifacts."""
        if self.description:
            return f"{self.display_name} [{self.description}]"
        return self.display_name


@dataclass(frozen=True)
class ResolvedModelProfileEntry:
    """Concrete model settings for one Mentor agent role."""

    role: str
    backend: str
    model_id: str
    api_base: str | None
    api_key: str | None
    api_key_source: str
    request_kwargs: dict[str, Any] | None = None
    model_key: str | None = None
    display_name: str | None = None

    def create_model(self):
        """Instantiate the configured smolagents model."""
        return create_model(
            model_id=self.model_id,
            backend=self.backend,
            api_key=self.api_key,
            api_base=self.api_base,
            **copy.deepcopy(self.request_kwargs or {}),
        )


@dataclass(frozen=True)
class ResolvedRuntimeModelProfile:
    """Resolved runtime model profile (role → model)."""

    key: str
    description: str
    models: dict[str, ResolvedModelProfileEntry]

    def create_models(self) -> dict[str, Any]:
        """Instantiate one model per agent role."""
        return {role: entry.create_model() for role, entry in self.models.items()}


def resolve_model(key: str, *, strict: bool = True) -> ResolvedModel:
    """Resolve one catalogue model key into a concrete connection."""
    registry = _model_registry()
    if key not in registry:
        raise ValueError(
            f"Unknown model '{key}'. Available models: {', '.join(list_models())}"
        )
    item = registry[key]

    display_name = _env_or(item, "display_name", "display_name_env_var") or key
    backend = _env_or(item, "backend", "backend_env_var") or "openai"
    model_id = _env_or(item, "model_id", "model_id_env_var")
    if not model_id:
        raise ValueError(f"Model '{key}' is missing model_id.")

    api_base_names = _as_env_names(item.get("api_base_env_var"))
    api_base, _ = _first_env(api_base_names)
    api_base = api_base or item.get("api_base")

    api_key_names = _as_env_names(item.get("api_key_env_vars"))
    api_key, api_key_source = _first_env(api_key_names)
    default_api_key = item.get("default_api_key")
    if api_key is None and default_api_key:
        api_key = default_api_key
    if not api_key_source and api_key_names:
        api_key_source = api_key_names[0]
    elif not api_key_source:
        api_key_source = "default_api_key" if default_api_key else "not_required"

    if strict and item.get("requires_api_key") and not api_key:
        label = ", ".join(api_key_names) or "configured API key env var"
        raise ValueError(f"Model '{key}' requires one of: {label}.")

    return ResolvedModel(
        key=key,
        description=str(item.get("description", "") or ""),
        display_name=display_name,
        backend=backend,
        model_id=model_id,
        api_base=api_base,
        api_key=api_key,
        api_key_source=api_key_source,
        request_kwargs=copy.deepcopy(item.get("request_kwargs")),
        default_api_key=default_api_key,
    )


def list_models(*, include_env_default: bool = True) -> list[str]:
    """Return available model catalogue keys."""
    keys = sorted(_model_registry())
    if include_env_default:
        return keys
    return [key for key in keys if key != "env_default"]


def list_model_profiles() -> list[str]:
    """Return available runtime model profile keys."""
    return sorted(_profile_registry())


def get_selected_model_profile(profile_name: str | None = None) -> str | None:
    """Return the selected runtime model profile key, if any."""
    selected = (profile_name or os.getenv("MENTOR_MODEL_PROFILE", "")).strip()
    return selected or None


def _entry_from_resolved(role: str, resolved: ResolvedModel) -> ResolvedModelProfileEntry:
    return ResolvedModelProfileEntry(
        role=role,
        backend=resolved.backend,
        model_id=resolved.model_id,
        api_base=resolved.api_base,
        api_key=resolved.api_key or resolved.default_api_key,
        api_key_source=resolved.api_key_source,
        request_kwargs=copy.deepcopy(resolved.request_kwargs),
        model_key=resolved.key,
        display_name=resolved.display_name,
    )


def _normalize_agents_map(agents: dict[str, Any]) -> dict[str, str]:
    """Expand agents map where values are model keys (strings)."""
    normalized: dict[str, str] = {}
    for role, value in agents.items():
        if role not in _SUPPORTED_KEYS:
            raise ValueError(f"Unsupported agent key '{role}'.")
        if not isinstance(value, str) or not value.strip():
            raise ValueError(
                f"Agent '{role}' must reference a model key string, got {value!r}."
            )
        normalized[role] = value.strip()
    return normalized


def resolve_profile(
    key_or_roles: str | dict[str, str],
    *,
    strict: bool = True,
) -> ResolvedRuntimeModelProfile:
    """
    Resolve a profile key or an inline role→model-key map.

    Roles not listed fall back to ``shared`` when present, else ``env_default``.
    """
    if isinstance(key_or_roles, dict):
        profile_key = "inline"
        description = "Inline role map"
        agents = _normalize_agents_map(key_or_roles)
    else:
        registry = _profile_registry()
        if key_or_roles not in registry:
            raise ValueError(
                f"Unknown model profile '{key_or_roles}'. "
                f"Available profiles: {', '.join(list_model_profiles())}"
            )
        raw = registry[key_or_roles]
        profile_key = raw["key"]
        description = raw.get("description", "")
        agents = _normalize_agents_map(raw.get("agents", {}))

    shared_key = agents.get("shared")
    shared_model = (
        resolve_model(shared_key, strict=strict) if shared_key else None
    )

    models: dict[str, ResolvedModelProfileEntry] = {}
    for role in MODEL_ROLES:
        if role in agents:
            models[role] = _entry_from_resolved(
                role, resolve_model(agents[role], strict=strict)
            )
        elif shared_model is not None:
            models[role] = replace(
                _entry_from_resolved(role, shared_model),
                role=role,
                request_kwargs=copy.deepcopy(shared_model.request_kwargs),
            )
        else:
            # Fall back to env_default when neither role nor shared is set.
            fallback = resolve_model("env_default", strict=strict)
            models[role] = _entry_from_resolved(role, fallback)

    return ResolvedRuntimeModelProfile(
        key=profile_key,
        description=description,
        models=models,
    )


def resolve_model_or_profile(
    key: str,
    *,
    strict: bool = True,
) -> ResolvedRuntimeModelProfile:
    """
    Resolve ``key`` as a **profile** (runs reference profiles only).

    Models are leaf connections inside ``model_profiles.json``; each runnable
    setup must be a profile that maps roles onto those model keys. Thin
    profiles with the same key as a model (``{"shared": "<model>"}``) cover
    single-model runs.
    """
    if key in _profile_registry():
        return resolve_profile(key, strict=strict)
    if key in _model_registry():
        raise ValueError(
            f"'{key}' is a model catalogue key, not a profile. "
            "Runs reference profiles only — add a profile that maps roles to "
            f"model '{key}', or use an existing profile "
            f"({', '.join(list_model_profiles())})."
        )
    raise ValueError(
        f"Unknown profile '{key}'. "
        f"Available profiles: {', '.join(list_model_profiles())}."
    )


def resolve_runtime_model_profile(
    profile_name: str | None = None,
    *,
    strict: bool = True,
) -> ResolvedRuntimeModelProfile | None:
    """Resolve a selected runtime model profile.

    Returns ``None`` when no profile was selected.
    """
    selected = get_selected_model_profile(profile_name)
    if not selected:
        return None
    return resolve_model_or_profile(selected, strict=strict)
