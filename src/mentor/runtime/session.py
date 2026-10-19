"""Shared run-session setup for production and experiment entrypoints.

Used by:
- ``mentor.cli`` (full pipeline) — resolves models from env / CLI / profile
- ``experiments.harness`` runners — usually ``resolve_models=False`` and attach
  their own Gatekeeper/Orchestrator models after session setup

Also defines ``review_to_json`` / ``protocol_to_json`` used when building a session.

Side effects (when requested):
- loads review JSON into the search store via ``load_review_data``
- creates a run output directory and configures workflow/activity loggers
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from smolagents import Model

from mentor.config import create_model, resolve_api_key, resolve_backend
from mentor.dataset import SystematicReview, load_review
from mentor.logging_utils import make_step_callbacks, setup_run_logging
from mentor.model_profiles import (
    get_selected_model_profile,
    resolve_runtime_model_profile,
)
from mentor.tools.search import load_review_data


def review_to_json(review: SystematicReview) -> str:
    """Full review JSON (protocol + studies) for the in-memory search store."""
    studies = [
        {
            "study_index": i + 1,
            "title": s.title,
            "abstract": s.abstract,
        }
        for i, s in enumerate(review.studies)
    ]
    data = {
        "title": review.title,
        "objective": review.objective,
        "background": review.background,
        "selection_criteria": review.selection_criteria,
        "n_total": len(studies),
        "studies": studies,
    }
    return json.dumps(data, ensure_ascii=False)


def protocol_to_json(review: SystematicReview) -> str:
    """Protocol-only JSON for orchestrator task text (no candidate studies)."""
    data = {
        "title": review.title,
        "objective": review.objective,
        "background": review.background,
        "selection_criteria": review.selection_criteria,
    }
    return json.dumps(data, ensure_ascii=False)


@dataclass
class RunLoggers:
    """Logger handles created for one run directory."""

    # Full chronological agent/workflow trace (workflow.log).
    agent_logger: Any
    # Human-readable phase summary (activity.md).
    activity_logger: Any


@dataclass
class RunSession:
    """Shared resources for a single pipeline or experiment run."""

    # Loaded Cochrane review (studies + protocol fields).
    review: SystematicReview
    # Output directory: report.md, evidence.json, logs, etc.
    run_dir: Path
    # Either one shared Model, a role→Model map, or None when unresolved.
    models: Model | dict[str, Model] | None
    loggers: RunLoggers
    # smolagents step callbacks wired to activity_logger.
    step_cbs: list
    # Full review JSON (protocol + studies) for the in-memory search store.
    review_json: str
    # Protocol-only JSON for orchestrator task text (no candidate studies).
    protocol_json: str
    # Effective backend label (e.g. openai / litellm) after resolution.
    backend: str
    # Role-keyed models when a profile or caller supplied them.
    models_by_role: dict[str, Model] | None = None
    # Model used for activity-summary / metadata helpers (usually orchestrator).
    activity_summary_model: Model | None = None
    # Profile key used, ``"env"`` for create_model path, or None if skipped.
    profile_key: str | None = None


@dataclass(frozen=True)
class _ResolvedModels:
    """Internal result of ``_resolve_models`` (mapped onto ``RunSession``)."""

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
    """Resolve which Model(s) a run should use.

    Priority (first match wins):
    - Skip — ``resolve_models=False`` and no models passed (experiments)
    - ``models_by_role`` — caller already built role→Model map
    - ``shared_model`` — one Model for every agent
    - ``model_profile`` — JSON runtime profile
    - Env/CLI — ``create_model(model_id, backend, api_base)``
    """
    # Default backend from env/CLI before any model-specific override.
    resolved_backend = resolve_backend(backend)

    # Experiments: session sets up review/logs only; models come later.
    if not resolve_models and models_by_role is None and shared_model is None:
        return _ResolvedModels(
            models=None,
            models_by_role=None,
            activity_summary_model=None,
            backend=resolved_backend,
            profile_key=None,
        )

    # Pre-built per-role models (e.g. different Gatekeeper vs Orchestrator).
    if models_by_role is not None:
        # Prefer orchestrator for activity summaries; else first available role.
        activity_summary_model = models_by_role.get("orchestrator") or next(
            iter(models_by_role.values())
        )
        if activity_summary_model is not None:
            # Some Model instances expose .backend; fall back to resolved_backend.
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

    # Single shared model for all agents.
    if shared_model is not None:
        return _ResolvedModels(
            models=shared_model,
            models_by_role=None,
            activity_summary_model=shared_model,
            backend=resolved_backend,
            profile_key=None,
        )

    # Named runtime profile from profiles.json.
    selected_profile = get_selected_model_profile(model_profile)
    # Profile owns backend/model_id/api_base; do not mix with CLI overrides.
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

    # Plain env/CLI model (OpenAI-compatible or LiteLLM).
    if resolve_backend(backend) == "openai" and not resolve_api_key():
        raise ValueError(
            "No API key resolved. Set MENTOR_API_KEY or OPENAI_API_KEY in .env."
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
    review_url: str,
    split: str,
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
    """Load a review, set up logging, and resolve models into a ``RunSession``.

    Model resolution options (first match wins):
    - ``models_by_role``: use as-is (experiment presets already resolved)
    - ``shared_model``: use as the single shared model
    - ``model_profile``: resolve a runtime profile
    - else: ``create_model(model_id=..., backend=..., api_base=...)``

    Experiment-only options (chunk size, suite, label policy, etc.) must stay
    outside this helper.
    """
    # Load the Cochrane review from the dataset split.
    review = load_review(review_url, split)
    if review is None:
        raise ValueError(
            f"Unable to load review '{review_url}' from split '{split}'."
        )

    # Serialize two views of the same review:
    # - review_json: protocol + studies → search store / Librarian tools
    # - protocol_json: protocol only → Orchestrator task (no pre-screening)
    review_json = review_to_json(review)
    protocol_json = protocol_to_json(review)
    if load_search_store:
        load_review_data(review_json)

    # Create run_dir and attach workflow + activity loggers.
    run_dir, agent_logger, activity_logger = setup_run_logging(
        review.title,
        include_subagent_steps=include_subagent_steps,
        output_root=output_root,
        run_name=run_name,
    )
    step_cbs = make_step_callbacks(activity_logger)
    loggers = RunLoggers(agent_logger=agent_logger, activity_logger=activity_logger)

    # Resolve models (or leave None when resolve_models=False).
    resolved = _resolve_models(
        resolve_models=resolve_models,
        model_id=model_id,
        backend=backend,
        api_base=api_base,
        model_profile=model_profile,
        shared_model=shared_model,
        models_by_role=models_by_role,
    )

    # Bundle everything the CLI / harness needs for this run.
    return RunSession(
        review=review,
        run_dir=run_dir,
        models=resolved.models,
        loggers=loggers,
        step_cbs=step_cbs,
        review_json=review_json,
        protocol_json=protocol_json,
        backend=resolved.backend,
        models_by_role=resolved.models_by_role,
        activity_summary_model=resolved.activity_summary_model,
        profile_key=resolved.profile_key,
    )
