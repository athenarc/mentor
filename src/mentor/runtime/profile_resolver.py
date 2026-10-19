"""
Resolve per-agent model settings from ``profiles.json`` (beside this module).

Profiles map orchestrator/librarian/gatekeeper/miner/critic roles to backend,
model id, API base/key (via env var names), and optional request kwargs.
When a profile defines ``shared``, that entry is cloned for any role without
its own block. Used by ``mentor.runtime.session`` and the production CLI.
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

MODEL_ROLES = ("orchestrator", "librarian", "gatekeeper", "miner", "critic")
_SUPPORTED_KEYS = frozenset(("shared", *MODEL_ROLES))
_DEFAULT_CONFIG_PATH = Path(__file__).resolve().parent / "profiles.json"


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
    return item[key]


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
    """Resolved runtime model profile for the Mentor workflow."""

    key: str
    description: str
    models: dict[str, ResolvedModelProfileEntry]

    def create_models(self) -> dict[str, Any]:
        """Instantiate one model per agent role."""
        return {role: entry.create_model() for role, entry in self.models.items()}


def _resolve_entry(
    role: str, item: dict[str, Any], *, strict: bool
) -> ResolvedModelProfileEntry:
    backend = _env_or(item, "backend", "backend_env_var")
    model_id = _env_or(item, "model_id", "model_id_env_var")

    api_base_names = _as_env_names(
        item.get("api_base_env_vars", item.get("api_base_env_var"))
    )
    api_base, _ = _first_env(api_base_names)
    api_base = api_base or item.get("api_base")

    api_key_names = _as_env_names(
        item.get("api_key_env_vars", item.get("api_key_env_var"))
    )
    api_key, api_key_source = _first_env(api_key_names)
    api_key_source = api_key_source or "not_required"

    if strict and item.get("requires_api_key") and not api_key:
        label = ", ".join(api_key_names) or "configured API key env var"
        raise ValueError(f"Model profile role '{role}' requires one of: {label}.")

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
def _profile_registry() -> dict[str, dict[str, Any]]:
    raw = os.getenv("MENTOR_MODEL_PROFILES_CONFIG", "").strip()
    path = Path(raw) if raw else _DEFAULT_CONFIG_PATH
    if raw and not path.is_absolute():
        path = _DEFAULT_CONFIG_PATH.parent / path
    with open(path, encoding="utf-8") as f:
        config = json.load(f)
    return {item["key"]: item for item in config.get("profiles", [])}


def get_selected_model_profile(profile_name: str | None = None) -> str | None:
    """Return the selected runtime model profile key, if any."""
    selected = (profile_name or os.getenv("MENTOR_MODEL_PROFILE", "")).strip()
    return selected or None


def list_model_profiles() -> list[str]:
    """Return available runtime model profile keys."""
    return sorted(_profile_registry())


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

    registry = _profile_registry()
    if selected not in registry:
        raise ValueError(
            f"Unknown model profile '{selected}'. "
            f"Available profiles: {', '.join(list_model_profiles())}"
        )

    raw = registry[selected]
    agents = raw.get("agents", {})
    unsupported = sorted(set(agents) - _SUPPORTED_KEYS)
    if unsupported:
        raise ValueError(
            f"Model profile '{selected}' contains unsupported agent keys: "
            f"{', '.join(unsupported)}"
        )

    shared = (
        _resolve_entry("shared", agents["shared"], strict=strict)
        if "shared" in agents
        else None
    )

    models: dict[str, ResolvedModelProfileEntry] = {}
    for role in MODEL_ROLES:
        if role in agents:
            models[role] = _resolve_entry(role, agents[role], strict=strict)
        elif shared is not None:
            models[role] = replace(
                shared,
                role=role,
                request_kwargs=copy.deepcopy(shared.request_kwargs),
            )
        else:
            raise ValueError(
                f"Model profile '{selected}' is missing configuration for role '{role}'."
            )

    return ResolvedRuntimeModelProfile(
        key=raw["key"],
        description=raw.get("description", ""),
        models=models,
    )
