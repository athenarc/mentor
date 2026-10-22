"""Shared run-session setup for Mentor entrypoints.

Loads one review from a JSON file (never the Cochrane CSV dataset), wires
logging, and resolves models (env / CLI / profile).

Side effects (when requested):
- loads review JSON into the search store via ``load_review_data``
- creates a run output directory and configures workflow/activity loggers
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from smolagents import Model

from mentor.logging import make_step_callbacks, setup_run_logging
from mentor.review import (
    SystematicReview,
    load_review_from_json,
    protocol_to_json,
    review_to_json,
)
from mentor.runtime.models import (
    MODEL_CONFIG_REQUIRED_MESSAGE,
    create_model,
    has_explicit_model_config,
    resolve_api_key,
    resolve_backend,
)
from mentor.runtime.profile_resolver import (
    get_selected_model_profile,
    resolve_runtime_model_profile,
)
from mentor.tools.search import load_review_data

# Re-export for callers that historically imported serializers from session.
__all__ = [
    "RunLoggers",
    "RunSession",
    "prepare_run_session",
    "protocol_to_json",
    "review_to_json",
]


@dataclass
class RunLoggers:
    """Logger handles created for one run directory."""

    agent_logger: Any
    activity_logger: Any


@dataclass
class RunSession:
    """Shared resources for a single Mentor run."""

    review: SystematicReview
    run_dir: Path
    models: Model | dict[str, Model] | None
    loggers: RunLoggers
    step_cbs: list
    protocol_json: str
    backend: str
    review_json_path: Path | None = None
    models_by_role: dict[str, Model] | None = None
    activity_summary_model: Model | None = None
    profile_key: str | None = None


@dataclass(frozen=True)
class _ResolvedModels:
    models: Model | dict[str, Model] | None
    models_by_role: dict[str, Model] | None
    activity_summary_model: Model | None
    backend: str
    profile_key: str | None


def _resolve_models(
    *,
    resolve_models: bool,
    model_id: str | None,
    backend: str | None,
    api_base: str | None,
    model_profile: str | None,
    shared_model: Model | None,
    models_by_role: dict[str, Model] | None,
) -> _ResolvedModels:
    resolved_backend = resolve_backend(backend)

    if not resolve_models and models_by_role is None and shared_model is None:
        return _ResolvedModels(
            models=None,
            models_by_role=None,
            activity_summary_model=None,
            backend=resolved_backend,
            profile_key=None,
        )

    if models_by_role is not None:
        activity_summary_model = models_by_role.get("orchestrator") or next(
            iter(models_by_role.values())
        )
        if activity_summary_model is not None:
            resolved_backend = (
                getattr(activity_summary_model, "backend", resolved_backend)
                or resolved_backend
            )
        return _ResolvedModels(
            models=models_by_role,
            models_by_role=models_by_role,
            activity_summary_model=activity_summary_model,
            backend=resolved_backend,
            profile_key=None,
        )

    if shared_model is not None:
        return _ResolvedModels(
            models=shared_model,
            models_by_role=None,
            activity_summary_model=shared_model,
            backend=resolved_backend,
            profile_key=None,
        )

    selected_profile = get_selected_model_profile(model_profile)
    if selected_profile and any([model_id, backend, api_base]):
        raise ValueError(
            "model_profile cannot be combined with model_id, backend, or api_base."
        )
    if selected_profile:
        profile = resolve_runtime_model_profile(selected_profile, strict=True)
        resolved_models_by_role = profile.create_models()
        return _ResolvedModels(
            models=resolved_models_by_role,
            models_by_role=resolved_models_by_role,
            activity_summary_model=resolved_models_by_role["orchestrator"],
            backend=profile.models["orchestrator"].backend,
            profile_key=profile.key,
        )

    if not has_explicit_model_config(model_id, backend, api_base):
        raise ValueError(MODEL_CONFIG_REQUIRED_MESSAGE)

    if resolve_backend(backend) == "openai" and not resolve_api_key():
        raise ValueError(
            "No API key resolved. Set MENTOR_API_KEY in .env."
        )
    model = create_model(model_id=model_id, backend=backend, api_base=api_base)
    return _ResolvedModels(
        models=model,
        models_by_role=None,
        activity_summary_model=model,
        backend=resolved_backend,
        profile_key="env",
    )


def prepare_run_session(
    *,
    review_json_path: str | Path,
    include_subagent_steps: bool = True,
    output_root: Path | None = None,
    run_name: str | None = None,
    load_search_store: bool = True,
    resolve_models: bool = True,
    model_id: str | None = None,
    backend: str | None = None,
    api_base: str | None = None,
    model_profile: str | None = None,
    shared_model: Model | None = None,
    models_by_role: dict[str, Model] | None = None,
) -> RunSession:
    """Load a review JSON file, set up logging, and resolve models."""
    path = Path(review_json_path)
    if not path.is_file():
        raise ValueError(f"Review JSON not found: {path}")

    review = load_review_from_json(path)
    review_json = review_to_json(review)
    protocol_json = protocol_to_json(review)

    # Fail fast on model config before creating a run directory.
    resolved = _resolve_models(
        resolve_models=resolve_models,
        model_id=model_id,
        backend=backend,
        api_base=api_base,
        model_profile=model_profile,
        shared_model=shared_model,
        models_by_role=models_by_role,
    )

    if load_search_store:
        load_review_data(review_json)

    run_dir, agent_logger, activity_logger = setup_run_logging(
        review.title,
        include_subagent_steps=include_subagent_steps,
        output_root=output_root,
        run_name=run_name,
    )
    step_cbs = make_step_callbacks(activity_logger)
    loggers = RunLoggers(agent_logger=agent_logger, activity_logger=activity_logger)

    return RunSession(
        review=review,
        run_dir=run_dir,
        models=resolved.models,
        loggers=loggers,
        step_cbs=step_cbs,
        protocol_json=protocol_json,
        backend=resolved.backend,
        review_json_path=path.resolve(),
        models_by_role=resolved.models_by_role,
        activity_summary_model=resolved.activity_summary_model,
        profile_key=resolved.profile_key,
    )
