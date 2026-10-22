"""Public API for running Mentor on one review JSON file."""

from __future__ import annotations

import json
import logging
import time
from pathlib import Path
from typing import Any

from smolagents import Model

from mentor.agents import create_orchestrator_agent
from mentor.logging.provider_usage import ProviderUsageCollector, attach_usage_collector
from mentor.review import pipeline_stages_for_mode
from mentor.runtime.models import resolve_api_base
from mentor.runtime.session import prepare_run_session

logger = logging.getLogger(__name__)

SCREENING_ONLY_TASK = """\
Conduct only title/abstract screening for this review.

Review title: {title}

Review background:
{background}

Review objective:
{objective}

Selection criteria:
{selection_criteria}

Output directory: {run_dir}
Expected study decisions: {n_studies}

Call screen_candidates() once, then return \
format_screening_progress_summary(review_title, output_dir) \
as final_answer.
"""

FULL_PIPELINE_TASK = """\
Conduct a systematic review for the following research question.

Review protocol (JSON):
{protocol_json}

Execute the full pipeline:
1. Use the librarian to retrieve candidate studies
2. Use get_candidates_json() to obtain a clean JSON of the candidates
3. Call screen_candidates() to screen studies for inclusion/exclusion
4. Use the miner to extract evidence from included studies
5. Use the critic to synthesize the evidence
6. Use format_report() to format a clean Markdown report
7. Use save_evidence_json() to save structured data \
(output_dir: "{run_dir}")

Return the formatted report as your final answer.
"""


def _write_run_json(run_dir: Path, payload: dict[str, Any]) -> Path:
    path = run_dir / "run.json"
    path.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")
    return path


def _save_report(report: str, run_dir: Path) -> Path:
    output_path = run_dir / "report.md"
    output_path.write_text(report, encoding="utf-8")
    return output_path


def run_review(
    *,
    review_json_path: str | Path,
    model_id: str | None = None,
    backend: str | None = None,
    api_base: str | None = None,
    model_profile: str | None = None,
    include_subagent_steps: bool = True,
    batch_size: int | None = None,
    output_root: Path | None = None,
    run_name: str | None = None,
    shared_model: Model | None = None,
    models_by_role: dict[str, Model] | None = None,
    extra_run_meta: dict[str, Any] | None = None,
    raise_on_error: bool = True,
) -> str:
    """Run the Mentor pipeline for one review JSON file.

    Pipeline mode comes from the review JSON ``mode`` field.

    Returns the orchestrator final answer (report text for full runs).
    When ``raise_on_error`` is False, failures are recorded in ``run.json``
    and this function returns ``""`` instead of re-raising.
    """
    logger.info("=" * 70)
    logger.info("MENTOR SYSTEMATIC REVIEW PIPELINE")
    logger.info("=" * 70)

    path = Path(review_json_path)
    session = prepare_run_session(
        review_json_path=path,
        include_subagent_steps=include_subagent_steps,
        output_root=output_root,
        run_name=run_name,
        model_id=model_id,
        backend=backend,
        api_base=api_base,
        model_profile=model_profile,
        shared_model=shared_model,
        models_by_role=models_by_role,
    )

    review = session.review
    mode = review.mode
    pipeline_stages = pipeline_stages_for_mode(mode)
    run_dir = session.run_dir
    activity_logger = session.loggers.activity_logger
    agent_logger = session.loggers.agent_logger
    step_cbs = session.step_cbs
    usage_collector = ProviderUsageCollector()
    step_cbs = attach_usage_collector(step_cbs, usage_collector)
    protocol_json = session.protocol_json
    _backend = session.backend
    _activity_summary_model = session.activity_summary_model

    logger.info(review.summary())
    logger.info("Run directory: %s", run_dir)
    logger.info("Mode: %s | batch_size: %s", mode, batch_size)
    activity_logger.log_metadata("Review JSON", str(path.resolve()))
    activity_logger.log_metadata("Mode", mode)
    activity_logger.log_metadata("Studies", str(len(review.studies)))
    activity_logger.log_metadata("Batch size", str(batch_size))
    if review.prompts:
        activity_logger.log_metadata(
            "Prompt overrides",
            ", ".join(f"{role}={path}" for role, path in sorted(review.prompts.items())),
        )

    role_models = session.models_by_role
    shared_model = None if role_models is not None else session.models
    orch_model = (
        role_models["orchestrator"] if role_models is not None else shared_model
    )
    logger.info(
        "Model backend: %s | orchestrator model_id: %s",
        _backend,
        orch_model.model_id,
    )
    if session.profile_key:
        logger.info("Model profile: %s", session.profile_key)
    activity_logger.log_metadata("Model Profile", session.profile_key or "env")
    activity_logger.log_metadata(
        "Orchestrator Model", f"{_backend} | {orch_model.model_id}"
    )
    if role_models is None:
        resolved_api_base = resolve_api_base(api_base)
        if resolved_api_base:
            activity_logger.log_metadata("Shared API Base", resolved_api_base)

    orchestrator = create_orchestrator_agent(
        model=shared_model,
        models_by_role=role_models,
        step_callbacks=step_cbs,
        logger=agent_logger,
        stages=pipeline_stages,
        batch_size=batch_size,
        output_dir=str(run_dir),
        prompt_paths=review.prompts or None,
    )

    if mode == "screening-only":
        task = SCREENING_ONLY_TASK.format(
            title=review.title,
            background=review.background,
            objective=review.objective,
            selection_criteria=review.selection_criteria,
            run_dir=run_dir,
            n_studies=len(review.studies),
        )
    else:
        task = FULL_PIPELINE_TASK.format(
            protocol_json=protocol_json,
            run_dir=run_dir,
        )

    logger.info("Starting orchestrated pipeline...")
    activity_logger.mark_pipeline_start()
    report = ""
    run_status = "completed"
    error = ""
    caught: BaseException | None = None
    started = time.perf_counter()

    try:
        result = orchestrator.run(task)
        logger.info("Pipeline complete!")
        report = str(result)
        if mode == "full":
            report_path = _save_report(report, run_dir)
            logger.info("Report saved to: %s", report_path)
        logger.info("\nFull logs at: %s", run_dir)
    except Exception as exc:
        caught = exc
        run_status = "error"
        error = f"{type(exc).__name__}: {exc}"
        logger.exception("Pipeline failed")
        report = ""
    finally:
        duration = time.perf_counter() - started
        activity_path = activity_logger.finalize(_activity_summary_model)
        logger.info("Activity log saved to: %s", activity_path)
        agent_logger.close()
        payload: dict[str, Any] = {
            "review_json": str(path.resolve()),
            "mode": mode,
            "stages": pipeline_stages,
            "prompt_overrides": dict(review.prompts) if review.prompts else {},
            "screening_batch_size": batch_size,
            "model_profile": session.profile_key,
            "status": run_status,
            "error": error,
            "duration_seconds": duration,
            "provider_usage": usage_collector.summary(),
            "n_studies": len(review.studies),
            "run_dir": str(run_dir),
        }
        if extra_run_meta:
            # Suite/caller fields first; this run's status/timing win.
            payload = {**extra_run_meta, **payload}
        _write_run_json(run_dir, payload)

    if caught is not None and raise_on_error:
        raise caught

    return report
