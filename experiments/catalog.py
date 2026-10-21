"""
Read Mentor's model_profiles.json for suite expansion / analyze labels.

Experiments never import ``mentor``; they only read the JSON catalogue on disk.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

from experiments.paths import MODEL_PROFILES_PATH

MODEL_ROLES = ("orchestrator", "librarian", "gatekeeper", "miner", "critic")


@dataclass(frozen=True)
class ResolvedModel:
    """Catalogue model metadata used in experiment artifacts."""

    key: str
    description: str
    display_name: str
    backend: str
    model_id: str
    api_base: str | None
    api_key: str | None = None
    api_key_source: str = ""
    request_kwargs: dict[str, Any] | None = None
    default_api_key: str | None = None

    @property
    def model_label(self) -> str:
        if self.description:
            return f"{self.display_name} [{self.description}]"
        return self.display_name


@dataclass(frozen=True)
class RoleModelMap:
    profile_key: str
    agents: dict[str, str]  # role → model catalogue key
    label: str


def _catalog_path() -> Path:
    env = os.getenv("MENTOR_MODELS_CONFIG", "").strip()
    if not env:
        return MODEL_PROFILES_PATH
    path = Path(env)
    if not path.is_absolute():
        path = MODEL_PROFILES_PATH.parent / path
    return path


@lru_cache(maxsize=1)
def _load_catalog() -> dict[str, Any]:
    with open(_catalog_path(), encoding="utf-8") as f:
        return json.load(f)


@lru_cache(maxsize=1)
def _model_registry() -> dict[str, dict[str, Any]]:
    return {item["key"]: item for item in _load_catalog().get("models", [])}


@lru_cache(maxsize=1)
def _profile_registry() -> dict[str, dict[str, Any]]:
    return {item["key"]: item for item in _load_catalog().get("profiles", [])}


def list_models(*, include_env_default: bool = True) -> list[str]:
    keys = sorted(_model_registry())
    if include_env_default:
        return keys
    return [key for key in keys if key != "env_default"]


def list_model_profiles() -> list[str]:
    return sorted(_profile_registry())


def resolve_model(key: str, *, strict: bool = True) -> ResolvedModel:
    registry = _model_registry()
    if key not in registry:
        if strict:
            raise ValueError(
                f"Unknown model '{key}'. Available: {', '.join(list_models())}"
            )
        return ResolvedModel(
            key=key,
            description="",
            display_name=key,
            backend="",
            model_id=key,
            api_base=None,
            api_key_source="",
        )
    item = registry[key]
    display_name = str(item.get("display_name") or key)
    return ResolvedModel(
        key=key,
        description=str(item.get("description") or ""),
        display_name=display_name,
        backend=str(item.get("backend") or "openai"),
        model_id=str(item.get("model_id") or key),
        api_base=(str(item["api_base"]).strip() if item.get("api_base") else None),
        api_key_source=str(item.get("api_key_env_var") or ""),
    )


def resolve_profile_agents(profile_key: str) -> RoleModelMap:
    """Expand a profile key into role → model-catalogue-key assignments."""
    registry = _profile_registry()
    if profile_key not in registry:
        if profile_key in _model_registry():
            agents = {role: profile_key for role in MODEL_ROLES}
            return RoleModelMap(
                profile_key=profile_key, agents=agents, label=profile_key
            )
        raise ValueError(
            f"Unknown profile '{profile_key}'. "
            f"Available: {', '.join(list_model_profiles())}"
        )

    raw = registry[profile_key]
    agents_raw = dict(raw.get("agents") or {})
    shared = agents_raw.get("shared")
    agents: dict[str, str] = {}
    for role in MODEL_ROLES:
        if role in agents_raw and isinstance(agents_raw[role], str):
            agents[role] = agents_raw[role].strip()
        elif shared:
            agents[role] = str(shared).strip()
        else:
            agents[role] = "env_default"
    return RoleModelMap(
        profile_key=str(raw.get("key") or profile_key),
        agents=agents,
        label=str(raw.get("key") or profile_key),
    )
