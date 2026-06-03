"""Runtime model-profile resolution for the Bastirr workflow."""

from __future__ import annotations

import copy
import json
import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

from bastirr.config import create_model


MODEL_ROLES = ("orchestrator", "librarian", "gatekeeper", "miner", "critic")
SUPPORTED_AGENT_KEYS = ("shared", *MODEL_ROLES)
_CONFIG_DIR = Path(__file__).resolve().parent / "runtime_config"
_DEFAULT_CONFIG_PATH = _CONFIG_DIR / "model_profiles.json"


def _normalize_env_var_names(value: str | list[str] | None) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    return [item for item in value if item]


def _resolve_env_value(env_var_names: list[str]) -> tuple[str | None, str | None]:
    for env_var in env_var_names:
        env_value = os.getenv(env_var, "").strip()
        if env_value:
            return env_value, env_var
    return None, None


@dataclass(frozen=True)
class ResolvedModelProfileEntry:
    """Concrete model settings for one Bastirr agent role."""

    role: str
    backend: str
    model_id: str
    api_base: str | None
    api_key: str | None
    api_key_source: str
    request_kwargs: dict[str, Any] | None = None

    def create_model(self):
        """Instantiate the configured smolagents model."""
        return create_model(
            model_id=self.model_id,
            backend=self.backend,
            api_key=self.api_key,
            api_base=self.api_base,
            **copy.deepcopy(self.request_kwargs or {}),
        )

    def with_role(self, role: str) -> "ResolvedModelProfileEntry":
        """Reuse the same resolved settings for another role."""
        return ResolvedModelProfileEntry(
            role=role,
            backend=self.backend,
            model_id=self.model_id,
            api_base=self.api_base,
            api_key=self.api_key,
            api_key_source=self.api_key_source,
            request_kwargs=copy.deepcopy(self.request_kwargs),
        )

    def metadata(self) -> dict[str, str]:
        """Return loggable, non-secret metadata for this entry."""
        return {
            "backend": self.backend,
            "model_id": self.model_id,
            "api_base": self.api_base or "",
            "api_key_source": self.api_key_source,
            "request_kwargs": json.dumps(self.request_kwargs or {}, sort_keys=True),
        }


@dataclass(frozen=True)
class ResolvedRuntimeModelProfile:
    """Resolved runtime model profile for the Bastirr workflow."""

    key: str
    description: str
    models: dict[str, ResolvedModelProfileEntry]

    def create_models(self) -> dict[str, Any]:
        """Instantiate one model per agent role."""
        return {
            role: entry.create_model()
            for role, entry in self.models.items()
        }


def _resolve_profile_entry(role: str, item: dict[str, Any], *, strict: bool) -> ResolvedModelProfileEntry:
    backend = (
        os.getenv(item.get("backend_env_var", ""), "").strip()
        if item.get("backend_env_var")
        else ""
    ) or item["backend"]
    model_id = (
        os.getenv(item.get("model_id_env_var", ""), "").strip()
        if item.get("model_id_env_var")
        else ""
    ) or item["model_id"]

    api_base_env_vars = _normalize_env_var_names(
        item.get("api_base_env_vars", item.get("api_base_env_var"))
    )
    api_base, _ = _resolve_env_value(api_base_env_vars)
    api_base = api_base or item.get("api_base")

    api_key_env_vars = _normalize_env_var_names(
        item.get("api_key_env_vars", item.get("api_key_env_var"))
    )
    api_key, api_key_source = _resolve_env_value(api_key_env_vars)
    api_key_source = api_key_source or "not_required"

    if strict and item.get("requires_api_key") and not api_key:
        env_var_label = ", ".join(api_key_env_vars) if api_key_env_vars else "configured API key env var"
        raise ValueError(
            f"Model profile role '{role}' requires one of: {env_var_label}."
        )

    return ResolvedModelProfileEntry(
        role=role,
        backend=backend,
        model_id=model_id,
        api_base=api_base,
        api_key=api_key,
        api_key_source=api_key_source,
        request_kwargs=copy.deepcopy(item.get("request_kwargs")),
    )


@lru_cache(maxsize=1)
def _get_config_path() -> Path:
    raw_path = os.getenv("BASTIRR_MODEL_PROFILES_CONFIG", "").strip()
    if not raw_path:
        return _DEFAULT_CONFIG_PATH

    candidate = Path(raw_path)
    if not candidate.is_absolute():
        candidate = _CONFIG_DIR / candidate
    return candidate


@lru_cache(maxsize=1)
def _load_model_profile_config() -> dict[str, Any]:
    with open(_get_config_path(), "r", encoding="utf-8") as f:
        return json.load(f)


@lru_cache(maxsize=1)
def _build_profile_registry() -> dict[str, dict[str, Any]]:
    config = _load_model_profile_config()
    registry: dict[str, dict[str, Any]] = {}
    for item in config.get("profiles", []):
        registry[item["key"]] = item
    return registry


def get_selected_model_profile(profile_name: str | None = None) -> str | None:
    """Return the selected runtime model profile key, if any."""
    selected = (profile_name or os.getenv("BASTIRR_MODEL_PROFILE", "")).strip()
    return selected or None


def list_model_profiles() -> list[str]:
    """Return available runtime model profile keys."""
    return sorted(_build_profile_registry())


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

    registry = _build_profile_registry()
    if selected not in registry:
        raise ValueError(
            f"Unknown model profile '{selected}'. Available profiles: {', '.join(list_model_profiles())}"
        )

    raw_profile = registry[selected]
    raw_agents = raw_profile.get("agents", {})
    unsupported = sorted(set(raw_agents) - set(SUPPORTED_AGENT_KEYS))
    if unsupported:
        raise ValueError(
            f"Model profile '{selected}' contains unsupported agent keys: {', '.join(unsupported)}"
        )

    shared_entry = None
    if "shared" in raw_agents:
        shared_entry = _resolve_profile_entry("shared", raw_agents["shared"], strict=strict)

    resolved_models: dict[str, ResolvedModelProfileEntry] = {}
    for role in MODEL_ROLES:
        if role in raw_agents:
            resolved_models[role] = _resolve_profile_entry(role, raw_agents[role], strict=strict)
            continue
        if shared_entry is not None:
            resolved_models[role] = shared_entry.with_role(role)
            continue
        raise ValueError(
            f"Model profile '{selected}' is missing configuration for role '{role}'."
        )

    return ResolvedRuntimeModelProfile(
        key=raw_profile["key"],
        description=raw_profile.get("description", ""),
        models=resolved_models,
    )
