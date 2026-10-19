"""
Batch Gatekeeper screening benchmark runner.

Executes the thin ``screening_orchestrator`` for each review × gatekeeper preset
× repeat, writes raw run dirs under ``raw_runs/``, materializes per-policy views
(include/exclude gold mappings), aggregates ``summary.csv`` / leaderboards, and
supports checkpointed reruns via ``benchmark_checkpoint.json``.

Public entrypoints: ``run_screening_review``, ``run_screening_benchmark``,
``rerun_screening_reviews_in_experiment``.
"""

from __future__ import annotations

import csv
import json
import logging
import os
import shutil
import time
from datetime import datetime
from pathlib import Path
from statistics import fmean

from experiments.harness.common import (
    metric_telemetry as _metric_telemetry,
    policy_dir_for_label as _policy_dir_for_label,
    policy_dir_name as _policy_dir_name,
    read_json as _read_json,
    resolve_existing_path as _resolve_existing_path,
    sort_raw_runs as _sort_raw_runs,
)
from experiments.harness.comparison_reports import write_policy_comparison_report
from experiments.prompts import load_prompt as load_exp_prompt
from mentor.agents.screening_orchestrator import create_screening_orchestrator_agent
from experiments.harness.html_reports import write_policy_html_report
from experiments.harness.inspection import write_screening_inspection_artifacts
from experiments.harness.metrics import SCREENING_LABEL_POLICIES, compute_screening_metrics
from experiments.harness.model_presets import (
    ResolvedModelPreset,
    get_model_preset,
    resolve_model_presets,
)
from experiments.harness.notebooks import write_policy_eda_notebook
from experiments.harness.provider_usage import ProviderUsageCollector, attach_usage_collector
from experiments.harness.review_suites import (
    ScreeningBenchmarkReview,
    resolve_review_selection,
)
from experiments.harness.telemetry import (
    collect_activity_telemetry,
    compute_rationale_metrics,
)
from experiments.harness.totals import register_canonical_sources_from_experiment
from mentor.config import OUTPUT_DIR
from mentor.dataset import load_review
from mentor.errors import ContextOverflowError
from mentor.runtime.session import prepare_run_session

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
)
logger = logging.getLogger("experiments.screening")

_MAX_SCREENING_ATTEMPTS = 2

_SUMMARY_CSV_PRIORITY_FIELDS = [
    "benchmark_run_id",
    "suite",
    "review_key",
    "review_title",
    "split",
    "n_studies",
    "benchmark_architecture",
    "run_index",
    "run_status",
    "error_type",
    "screening_completion_status",
    "scored_for_aggregate",
    "screening_attempt_count",
    "rerun_triggered",
    "incomplete_reason",
    "gatekeeper_preset",
    "gatekeeper_model_label",
    "orchestrator_policy",
    "orchestrator_preset",
    "orchestrator_model_label",
    "gold_label_policy",
    "predicted_pass_count",
    "gold_pass_count",
    "predicted_exclude_count",
    "gold_exclude_count",
    "tp",
    "fp",
    "tn",
    "fn",
    "accuracy",
    "precision",
    "recall",
    "specificity",
    "f1",
    "decision_coverage",
    "parse_success",
    "screening_decision_count",
    "missing_decision_count",
    "duplicate_decision_count",
    "invalid_decision_count",
    "duration_seconds",
    "duration_per_study_seconds",
    "total_input_tokens",
    "total_output_tokens",
    "total_tokens",
    "total_steps",
    "orchestrator_step_count",
    "gatekeeper_step_count",
    "error_step_count",
    "retry_count",
    "resume_count",
    "empty_rationale_count",
    "duplicate_rationale_count",
    "rationale_reuse_rate",
    "error",
    "review_url",
    "run_dir",
    "screening_inspection_json",
    "screening_inspection_markdown",
    "gatekeeper_backend",
    "gatekeeper_model_id",
    "gatekeeper_api_base",
    "gatekeeper_api_key_source",
    "orchestrator_backend",
    "orchestrator_model_id",
    "orchestrator_api_base",
    "orchestrator_api_key_source",
    "gold_label_policy_description",
]


def _experiment_root(suite_name: str) -> Path:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = OUTPUT_DIR / "screening_benchmarks" / f"{timestamp}_{suite_name}"
    path.mkdir(parents=True, exist_ok=True)
    return path


def _raw_runs_checkpoint_root(experiment_dir: Path) -> Path:
    path = experiment_dir / "_raw_runs"
    path.mkdir(parents=True, exist_ok=True)
    return path


def _link_or_copy(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    try:
        if src.exists() and dst.exists() and os.path.samefile(src, dst):
            return
    except OSError:
        pass
    if src.resolve(strict=False) == dst.resolve(strict=False):
        return
    if dst.exists() or dst.is_symlink():
        dst.unlink()
    try:
        os.link(src, dst)
    except OSError:
        shutil.copy2(src, dst)


def _atomic_write(path: Path, write_fn) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    try:
        write_fn(tmp_path)
        os.replace(tmp_path, path)
    finally:
        if tmp_path.exists():
            tmp_path.unlink()


def _run_name(
    review_case: ScreeningBenchmarkReview,
    gatekeeper_model: ResolvedModelPreset,
    orchestrator_policy: str,
    orchestrator_model: ResolvedModelPreset,
    run_index: int,
) -> str:
    return "_".join([
        review_case.key,
        gatekeeper_model.key,
        orchestrator_policy,
        orchestrator_model.key,
        f"run{run_index}",
    ])


def _build_screening_task_with_retry_note(
    review,
    output_dir: Path,
    expected_n_studies: int,
    retry_note: str | None = None,
) -> str:
    retry_block = ""
    if retry_note:
        retry_block = (
            "Retry guidance:\n"
            f"{retry_note}\n\n"
        )
    return (
        "Conduct only the title/abstract screening phase for this review.\n\n"
        f"Review title: {review.title}\n\n"
        f"Review background:\n{review.background}\n\n"
        f"Review objective:\n{review.objective}\n\n"
        f"Selection criteria:\n{review.selection_criteria}\n\n"
        f"Output directory: {output_dir}\n\n"
        f"Expected study decisions: {expected_n_studies}\n\n"
        f"{retry_block}"
        "Execute the screening-only pipeline:\n"
        "1. Use get_candidates_json() to retrieve the preloaded candidate studies.\n"
        "2. Call gatekeeper(task=\"\", additional_args={\"screening_payload\": candidates_json}); "
        "task text is ignored by the gatekeeper wrapper.\n"
        "3. Use save_screening_evidence_json() to save evidence.json in the output directory, "
        "passing expected_n_studies exactly.\n"
        "4. Use format_screening_summary() and return the summary as the final answer.\n"
        "Do not construct screening decisions inside orchestrator code. If the Gatekeeper output "
        "is incomplete or invalid, rerun the Gatekeeper instead of creating a fallback list.\n"
    )


def _screening_completion_status(metrics: dict) -> str:
    if metrics.get("parse_success"):
        return "complete"
    if metrics.get("screening_decision_count", 0) == 0:
        return "none"
    return "partial"


def _build_incomplete_reason(metrics: dict) -> str:
    if metrics.get("parse_success"):
        return ""
    return (
        f"Parsed {metrics.get('screening_decision_count', 0)}/"
        f"{metrics.get('n_studies', 0)} unique decisions "
        f"(missing={metrics.get('missing_decision_count', 0)}, "
        f"duplicate={metrics.get('duplicate_decision_count', 0)}, "
        f"invalid={metrics.get('invalid_decision_count', 0)})."
    )


def _build_retry_note(metrics: dict) -> str:
    return (
        "The previous attempt did not produce a complete screening output. "
        f"It yielded {metrics.get('screening_decision_count', 0)} unique decisions "
        f"for {metrics.get('n_studies', 0)} studies. "
        "Return exactly one decision object for every study index from 1 to n_total. "
        "Do not summarize excluded studies in bulk. Do not omit any study index. "
        "Do not return only included studies. The saved evidence.json must contain "
        "a complete per-study decision list."
    )


def _validate_review_case(
    review_case: ScreeningBenchmarkReview,
    review,
    *,
    label_policy: str,
) -> None:
    gold_metrics = compute_screening_metrics(
        review,
        screening_decisions=[],
        label_policy=label_policy,
    )
    actual_studies = gold_metrics["n_studies"]
    actual_screen_pass = gold_metrics["gold_pass_count"]
    actual_screen_exclude = gold_metrics["gold_exclude_count"]

    if actual_studies != review_case.expected_n_studies:
        raise ValueError(
            f"Review '{review_case.key}' expected {review_case.expected_n_studies} "
            f"studies, found {actual_studies}."
        )
    if (
        label_policy == "include_label_0_5"
        and actual_screen_pass != review_case.expected_n_screen_pass
    ):
        raise ValueError(
            f"Review '{review_case.key}' expected {review_case.expected_n_screen_pass} "
            f"screen-pass studies, found {actual_screen_pass}."
        )
    if (
        label_policy == "include_label_0_5"
        and actual_screen_exclude != review_case.expected_n_screen_exclude
    ):
        raise ValueError(
            f"Review '{review_case.key}' expected {review_case.expected_n_screen_exclude} "
            f"screen exclusions, found {actual_screen_exclude}."
        )


def _read_screening_decisions(evidence_path: Path) -> list[dict]:
    if not evidence_path.exists():
        return []
    with open(evidence_path, "r", encoding="utf-8") as f:
        payload = json.load(f)
    decisions = payload.get("screening_decisions", [])
    return decisions if isinstance(decisions, list) else []


def _context_overflow_run_status(
    *,
    decision_count: int,
    error: str = "",
    last_attempt_error: str = "",
) -> tuple[str, str]:
    """Map a context-overflow abort to (run_status, error)."""
    run_status = "incomplete" if decision_count > 0 else "error"
    return run_status, error or last_attempt_error


def _attach_context_overflow_telemetry(telemetry: dict, *, error_type: str) -> None:
    telemetry["context_overflow"] = error_type == "context_overflow"


def _build_run_metrics(
    *,
    review_case: ScreeningBenchmarkReview,
    review,
    screening_decisions: list[dict],
    gatekeeper_model: ResolvedModelPreset,
    orchestrator_model: ResolvedModelPreset,
    orchestrator_policy: str,
    suite_name: str,
    run_index: int,
    duration_seconds: float,
    run_dir: Path,
    run_status: str,
    label_policy: str,
    screening_attempt_count: int,
    rerun_triggered: bool,
    benchmark_architecture: str = "batch_orchestrator_v1",
    telemetry: dict | None = None,
    error: str = "",
    error_type: str = "",
) -> dict:
    metrics = compute_screening_metrics(
        review,
        screening_decisions,
        label_policy=label_policy,
    )
    completion_status = _screening_completion_status(metrics)
    scored_for_aggregate = run_status == "completed" and metrics["parse_success"]
    incomplete_reason = ""
    if run_status == "error":
        incomplete_reason = error or _build_incomplete_reason(metrics)
    elif not scored_for_aggregate:
        incomplete_reason = _build_incomplete_reason(metrics)
    metrics.update({
        "benchmark_run_id": _run_name(
            review_case,
            gatekeeper_model,
            orchestrator_policy,
            orchestrator_model,
            run_index,
        ),
        "suite": suite_name,
        "review_key": review_case.key,
        "review_title": review.title,
        "review_url": review.review_url,
        "split": review_case.split,
        "benchmark_architecture": benchmark_architecture,
        "run_index": run_index,
        "run_status": run_status,
        "error": error,
        "error_type": error_type,
        "screening_completion_status": completion_status,
        "scored_for_aggregate": scored_for_aggregate,
        "screening_attempt_count": screening_attempt_count,
        "rerun_triggered": rerun_triggered,
        "incomplete_reason": incomplete_reason,
        "duration_seconds": duration_seconds,
        "run_dir": str(run_dir),
        "gatekeeper_preset": gatekeeper_model.key,
        "gatekeeper_model_label": gatekeeper_model.model_label,
        "gatekeeper_backend": gatekeeper_model.backend,
        "gatekeeper_model_id": gatekeeper_model.model_id,
        "gatekeeper_api_base": gatekeeper_model.api_base or "",
        "gatekeeper_api_key_source": gatekeeper_model.api_key_source,
        "orchestrator_policy": orchestrator_policy,
        "orchestrator_preset": orchestrator_model.key,
        "orchestrator_model_label": orchestrator_model.model_label,
        "orchestrator_backend": orchestrator_model.backend,
        "orchestrator_model_id": orchestrator_model.model_id,
        "orchestrator_api_base": orchestrator_model.api_base or "",
        "orchestrator_api_key_source": orchestrator_model.api_key_source,
    })
    metrics.update(compute_rationale_metrics(screening_decisions))
    if telemetry:
        metrics.update(telemetry)
    return metrics


def _write_metrics_json(run_dir: Path, metrics: dict) -> None:
    def _write(path: Path) -> None:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(metrics, f, ensure_ascii=False, indent=2)

    _atomic_write(run_dir / "metrics.json", _write)


def _write_screening_evidence_file(run_dir: Path, screening_decisions: list[dict]) -> None:
    def _write(path: Path) -> None:
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"screening_decisions": screening_decisions}, f, ensure_ascii=False, indent=2)

    _atomic_write(run_dir / "evidence.json", _write)


def _materialize_policy_run_dir(raw_run_dir: Path, policy_run_dir: Path) -> None:
    policy_run_dir.mkdir(parents=True, exist_ok=True)
    for filename in ("workflow.log", "activity.md", "screening_progress.json"):
        source = raw_run_dir / filename
        if source.exists():
            _link_or_copy(source, policy_run_dir / filename)


# ---------------------------------------------------------------------------
# Single review run (batch architecture)
# ---------------------------------------------------------------------------

def run_screening_review(
    *,
    suite_name: str,
    review_case: ScreeningBenchmarkReview,
    gatekeeper_model: ResolvedModelPreset,
    orchestrator_model: ResolvedModelPreset,
    orchestrator_policy: str,
    run_index: int,
    output_root: Path,
    label_policy: str,
    include_subagent_steps: bool = True,
    orchestrator_max_steps: int = 20,
) -> dict:
    """
    Execute one screening benchmark run for a single review/model pair.
    """
    review = load_review(review_case.review_url, review_case.split)
    if review is None:
        raise ValueError(
            f"Unable to load review '{review_case.review_url}' from split '{review_case.split}'."
        )
    _validate_review_case(review_case, review, label_policy=label_policy)

    session = prepare_run_session(
        review_url=review_case.review_url,
        split=review_case.split,
        include_subagent_steps=include_subagent_steps,
        output_root=output_root,
        run_name=_run_name(
            review_case,
            gatekeeper_model,
            orchestrator_policy,
            orchestrator_model,
            run_index,
        ),
        resolve_models=False,
    )
    review = session.review
    run_dir = session.run_dir
    agent_logger = session.loggers.agent_logger
    activity_logger = session.loggers.activity_logger
    step_callbacks = session.step_cbs
    usage_collector = ProviderUsageCollector()
    step_callbacks = attach_usage_collector(step_callbacks, usage_collector)

    activity_logger.log_metadata("Benchmark suite", suite_name)
    activity_logger.log_metadata("Review key", review_case.key)
    activity_logger.log_metadata("Review URL", review.review_url)
    activity_logger.log_metadata("Dataset split", review_case.split)
    activity_logger.log_metadata("Studies", str(len(review.studies)))
    activity_logger.log_metadata("Gatekeeper preset", gatekeeper_model.key)
    activity_logger.log_metadata("Gatekeeper model", gatekeeper_model.model_label)
    activity_logger.log_metadata("Orchestrator preset", orchestrator_model.key)
    activity_logger.log_metadata("Orchestrator model", orchestrator_model.model_label)
    activity_logger.log_metadata("Orchestrator policy", orchestrator_policy)
    activity_logger.log_metadata("Gold label policy", label_policy)

    run_status = "completed"
    error = ""
    error_type = ""
    evidence_path = run_dir / "evidence.json"
    screening_attempt_count = 0
    rerun_triggered = False
    decisions: list[dict] = []
    last_attempt_error = ""
    telemetry: dict = {}

    activity_logger.mark_pipeline_start()
    started_at = time.perf_counter()
    try:
        retry_note = None
        for attempt_index in range(1, _MAX_SCREENING_ATTEMPTS + 1):
            screening_attempt_count = attempt_index
            if attempt_index > 1:
                rerun_triggered = True
                retry_message = (
                    f"Retrying screening attempt {attempt_index}/{_MAX_SCREENING_ATTEMPTS} "
                    f"because the previous attempt returned an incomplete decision set."
                )
                logger.warning(
                    "%s review=%s gatekeeper=%s",
                    retry_message,
                    review_case.key,
                    gatekeeper_model.key,
                )
                agent_logger.log(retry_message)

            try:
                screening_orchestrator = create_screening_orchestrator_agent(
                    orchestrator_model.create_model(),
                    gatekeeper_model.create_model(),
                    step_callbacks=step_callbacks,
                    logger=agent_logger,
                    max_steps=orchestrator_max_steps,
                    instructions=load_exp_prompt("screening_orchestrator"),
                )
                screening_orchestrator.run(
                    _build_screening_task_with_retry_note(
                        review,
                        run_dir,
                        expected_n_studies=len(review.studies),
                        retry_note=retry_note,
                    )
                )
            except ContextOverflowError as overflow_exc:
                last_attempt_error = f"{type(overflow_exc).__name__}: {overflow_exc}"
                error_type = "context_overflow"
                error = last_attempt_error
                logger.error(
                    "Context overflow during screening: review=%s gatekeeper=%s error=%s",
                    review_case.key,
                    gatekeeper_model.key,
                    last_attempt_error,
                )
                break
            except Exception as attempt_exc:
                last_attempt_error = f"{type(attempt_exc).__name__}: {attempt_exc}"
                if attempt_index == _MAX_SCREENING_ATTEMPTS:
                    raise
                retry_note = (
                    "The previous attempt failed before a complete evidence save. "
                    f"Error: {last_attempt_error} "
                    "Rerun the Gatekeeper and save only the raw Gatekeeper response. "
                    "Do not construct decisions in orchestrator code."
                )
                continue

            decisions = _read_screening_decisions(evidence_path)
            attempt_metrics = compute_screening_metrics(
                review,
                decisions,
                label_policy=label_policy,
            )
            if attempt_metrics["parse_success"]:
                break
            retry_note = _build_retry_note(attempt_metrics)
        else:
            run_status = "incomplete"
            if last_attempt_error and not error:
                error = last_attempt_error

        if error_type == "context_overflow":
            decisions = _read_screening_decisions(evidence_path)
            run_status, error = _context_overflow_run_status(
                decision_count=len(decisions),
                error=error,
                last_attempt_error=last_attempt_error,
            )
    except Exception as exc:
        run_status = "error"
        error = f"{type(exc).__name__}: {exc}"
        logger.exception(
            "Screening benchmark run failed for review=%s gatekeeper=%s",
            review_case.key,
            gatekeeper_model.key,
        )
    finally:
        duration_seconds = time.perf_counter() - started_at
        activity_path = activity_logger.finalize(model=None)
        telemetry = collect_activity_telemetry(
            activity_logger,
            duration_seconds=duration_seconds,
            n_studies=len(review.studies),
            retry_count=max(screening_attempt_count - 1, 0),
            resume_count=0,
        )
        _attach_context_overflow_telemetry(telemetry, error_type=error_type)
        telemetry.update(usage_collector.summary())
        telemetry["temperature"] = (gatekeeper_model.request_kwargs or {}).get("temperature")
        logger.info("Activity log saved to: %s", activity_path)
        agent_logger.close()

    decisions = _read_screening_decisions(evidence_path)
    return {
        "suite_name": suite_name,
        "review_case": review_case,
        "review": review,
        "screening_decisions": decisions,
        "gatekeeper_model": gatekeeper_model,
        "orchestrator_model": orchestrator_model,
        "orchestrator_policy": orchestrator_policy,
        "run_index": run_index,
        "duration_seconds": duration_seconds,
        "raw_run_dir": run_dir,
        "run_status": run_status,
        "error": error,
        "error_type": error_type,
        "screening_attempt_count": screening_attempt_count,
        "rerun_triggered": rerun_triggered,
        "benchmark_architecture": "batch_orchestrator_v1",
        "telemetry": telemetry,
    }


def _build_policy_run_metrics(
    raw_run: dict,
    *,
    label_policy: str,
    policy_run_dir: Path,
) -> dict:
    metrics = _build_run_metrics(
        review_case=raw_run["review_case"],
        review=raw_run["review"],
        screening_decisions=raw_run["screening_decisions"],
        gatekeeper_model=raw_run["gatekeeper_model"],
        orchestrator_model=raw_run["orchestrator_model"],
        orchestrator_policy=raw_run["orchestrator_policy"],
        suite_name=raw_run["suite_name"],
        run_index=raw_run["run_index"],
        duration_seconds=raw_run["duration_seconds"],
        run_dir=policy_run_dir,
        run_status=raw_run["run_status"],
        label_policy=label_policy,
        screening_attempt_count=raw_run["screening_attempt_count"],
        rerun_triggered=raw_run["rerun_triggered"],
        benchmark_architecture=raw_run.get("benchmark_architecture", "batch_orchestrator_v1"),
        telemetry=raw_run.get("telemetry"),
        error=raw_run["error"],
        error_type=raw_run.get("error_type", ""),
    )
    metrics.update(
        write_screening_inspection_artifacts(
            run_dir=policy_run_dir,
            review=raw_run["review"],
            screening_decisions=raw_run["screening_decisions"],
            metrics=metrics,
        )
    )
    _write_metrics_json(policy_run_dir, metrics)
    return metrics


def _materialize_policy_outputs(
    experiment_dir: Path,
    *,
    suite_name: str,
    repeats: int,
    review_keys: list[str],
    model_presets: list[str],
    orchestrator_policy: str,
    orchestrator_preset: str,
    label_policy: str,
    raw_runs: list[dict],
) -> tuple[Path, dict]:
    policy_dir = experiment_dir / _policy_dir_name(label_policy)
    policy_dir.mkdir(parents=True, exist_ok=True)

    run_metrics: list[dict] = []
    for raw_run in raw_runs:
        run_name = _run_name(
            raw_run["review_case"],
            raw_run["gatekeeper_model"],
            raw_run["orchestrator_policy"],
            raw_run["orchestrator_model"],
            raw_run["run_index"],
        )
        policy_run_dir = policy_dir / "runs" / run_name
        _materialize_policy_run_dir(raw_run["raw_run_dir"], policy_run_dir)
        _write_screening_evidence_file(policy_run_dir, raw_run["screening_decisions"])
        run_metrics.append(
            _build_policy_run_metrics(
                raw_run,
                label_policy=label_policy,
                policy_run_dir=policy_run_dir,
            )
        )

    aggregates = _aggregate_runs(run_metrics)
    review_aggregates = _aggregate_runs_by_review(run_metrics)
    summary = _write_summary_json(
        policy_dir,
        suite_name=suite_name,
        repeats=repeats,
        review_keys=review_keys,
        model_presets=model_presets,
        orchestrator_policy=orchestrator_policy,
        orchestrator_preset=orchestrator_preset,
        gold_label_policy=label_policy,
        run_metrics=run_metrics,
        aggregates=aggregates,
        review_aggregates=review_aggregates,
    )
    _write_summary_csv(policy_dir, run_metrics)
    _write_leaderboard_markdown(policy_dir, aggregates)
    _write_review_leaderboard_markdown(policy_dir, review_aggregates)
    return policy_dir, summary


def _policy_output_record(
    policy_dir: Path,
    summary: dict,
    *,
    notebook_info: dict | None = None,
    html_report_info: dict | None = None,
) -> dict:
    notebook_info = notebook_info or {}
    html_report_info = html_report_info or {}
    return {
        "directory": str(policy_dir),
        "summary_json": str(policy_dir / "summary.json"),
        "summary_csv": str(policy_dir / "summary.csv"),
        "leaderboard_markdown": str(policy_dir / "leaderboard.md"),
        "review_leaderboard_markdown": str(policy_dir / "review_leaderboard.md"),
        "runs_dir": str(policy_dir / "runs"),
        "html_report": html_report_info.get("report_path", ""),
        "eda_notebook": notebook_info.get("notebook_path", ""),
        "eda_notebook_executed": bool(notebook_info.get("executed", False)),
        "eda_notebook_execution_error": notebook_info.get("execution_error", ""),
        "summary": summary,
    }


def _checkpoint_policy_outputs(
    experiment_dir: Path,
    *,
    suite_name: str,
    repeats: int,
    review_keys: list[str],
    model_presets: list[str],
    orchestrator_policy: str,
    orchestrator_preset: str,
    selected_label_policies: list[str],
    raw_runs: list[dict],
) -> dict[str, dict]:
    policy_summaries: dict[str, dict] = {}
    for label_policy in selected_label_policies:
        policy_dir, summary = _materialize_policy_outputs(
            experiment_dir,
            suite_name=suite_name,
            repeats=repeats,
            review_keys=review_keys,
            model_presets=model_presets,
            orchestrator_policy=orchestrator_policy,
            orchestrator_preset=orchestrator_preset,
            label_policy=label_policy,
            raw_runs=raw_runs,
        )
        policy_summaries[label_policy] = _policy_output_record(policy_dir, summary)
    return policy_summaries


def _write_benchmark_checkpoint(
    experiment_dir: Path,
    *,
    suite_name: str,
    benchmark_architecture: str,
    repeats: int,
    review_keys: list[str],
    model_presets: list[str],
    orchestrator_policy: str,
    orchestrator_preset: str,
    selected_label_policies: list[str],
    total_expected_raw_runs: int,
    raw_runs: list[dict],
    policy_summaries: dict[str, dict],
    comparison_report: str | None = None,
    extra_metadata: dict | None = None,
) -> None:
    completed_runs = []
    for raw_run in raw_runs:
        completed_runs.append({
            "benchmark_run_id": _run_name(
                raw_run["review_case"],
                raw_run["gatekeeper_model"],
                raw_run["orchestrator_policy"],
                raw_run["orchestrator_model"],
                raw_run["run_index"],
            ),
            "review_key": raw_run["review_case"].key,
            "gatekeeper_preset": raw_run["gatekeeper_model"].key,
            "orchestrator_policy": raw_run["orchestrator_policy"],
            "orchestrator_preset": raw_run["orchestrator_model"].key,
            "run_index": raw_run["run_index"],
            "run_status": raw_run["run_status"],
            "raw_run_dir": str(raw_run["raw_run_dir"]),
        })
    payload = {
        "generated_at": datetime.now().isoformat(),
        "suite": suite_name,
        "benchmark_architecture": benchmark_architecture,
        "repeats": repeats,
        "review_keys": review_keys,
        "model_presets": model_presets,
        "orchestrator_policy": orchestrator_policy,
        "orchestrator_preset": orchestrator_preset,
        "gold_label_policies": selected_label_policies,
        "raw_runs_dir": str(_raw_runs_checkpoint_root(experiment_dir)),
        "completed_raw_run_count": len(raw_runs),
        "total_expected_raw_runs": total_expected_raw_runs,
        "completed_runs": completed_runs,
        "comparison_html_report": comparison_report,
        "policy_outputs": {
            policy: {
                key: value
                for key, value in record.items()
                if key != "summary"
            }
            for policy, record in policy_summaries.items()
        },
    }
    if extra_metadata:
        payload.update(extra_metadata)
    def _write(path: Path) -> None:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)

    _atomic_write(experiment_dir / "benchmark_checkpoint.json", _write)


def _source_policy_summary_for_rerun(
    experiment_dir: Path,
    *,
    selected_label_policies: list[str],
) -> tuple[str, Path, dict]:
    for label_policy in selected_label_policies:
        policy_dir = _policy_dir_for_label(experiment_dir, label_policy)
        summary_path = policy_dir / "summary.json"
        if summary_path.exists():
            return label_policy, policy_dir, _read_json(summary_path)
    raise FileNotFoundError(
        f"Expected at least one policy summary under: {experiment_dir}"
    )


def _run_source_dir_for_summary_row(
    experiment_dir: Path,
    policy_dir: Path,
    row: dict,
) -> Path:
    run_id = row["benchmark_run_id"]
    candidates: list[Path] = []
    if row.get("run_dir"):
        candidates.append(_resolve_existing_path(row["run_dir"]))
    candidates.append(policy_dir / "runs" / run_id)
    candidates.append(experiment_dir / "_raw_runs" / run_id)
    for candidate in candidates:
        if (candidate / "evidence.json").exists():
            return candidate
    raise FileNotFoundError(
        f"Could not find evidence.json for run '{run_id}' under {experiment_dir}."
    )


def _load_existing_batch_raw_runs(
    experiment_dir: Path,
    *,
    checkpoint: dict | None,
    selected_label_policies: list[str],
) -> tuple[list[dict], dict]:
    source_label_policy, policy_dir, summary = _source_policy_summary_for_rerun(
        experiment_dir,
        selected_label_policies=selected_label_policies,
    )
    suite_name = checkpoint.get("suite") if checkpoint else summary["suite"]
    review_keys = (
        checkpoint.get("review_keys")
        if checkpoint
        else summary.get("review_keys")
    ) or []
    if not review_keys:
        review_keys = list(dict.fromkeys(row["review_key"] for row in summary.get("runs", [])))
    model_presets = (
        checkpoint.get("model_presets")
        if checkpoint
        else summary.get("model_presets")
    ) or []
    if not model_presets:
        model_presets = list(dict.fromkeys(row["gatekeeper_preset"] for row in summary.get("runs", [])))
    orchestrator_policy = (
        checkpoint.get("orchestrator_policy")
        if checkpoint
        else summary["orchestrator_policy"]
    )
    orchestrator_preset = (
        checkpoint.get("orchestrator_preset")
        if checkpoint
        else summary["orchestrator_preset"]
    )
    repeats = int((checkpoint.get("repeats") if checkpoint else summary.get("repeats")) or 1)

    review_case_by_key = {
        review.key: review
        for review in resolve_review_selection(suite_name, review_keys or None)
    }
    raw_runs: list[dict] = []
    for row in summary.get("runs", []):
        run_id = row["benchmark_run_id"]
        review_key = row["review_key"]
        review_case = review_case_by_key.get(review_key)
        if review_case is None:
            raise ValueError(
                f"Run '{run_id}' references review '{review_key}', which is not in suite '{suite_name}'."
            )
        review = load_review(review_case.review_url, review_case.split)
        if review is None:
            raise ValueError(
                f"Unable to load review '{review_case.review_url}' from split '{review_case.split}'."
            )
        run_source_dir = _run_source_dir_for_summary_row(experiment_dir, policy_dir, row)
        metrics_path = run_source_dir / "metrics.json"
        metrics = dict(row)
        if metrics_path.exists():
            metrics.update(_read_json(metrics_path))

        raw_runs.append({
            "suite_name": suite_name,
            "review_case": review_case,
            "review": review,
            "screening_decisions": _read_screening_decisions(run_source_dir / "evidence.json"),
            "gatekeeper_model": get_model_preset(metrics["gatekeeper_preset"]).resolve(),
            "orchestrator_model": get_model_preset(metrics["orchestrator_preset"]).resolve(),
            "orchestrator_policy": metrics["orchestrator_policy"],
            "run_index": int(metrics["run_index"]),
            "duration_seconds": float(metrics.get("duration_seconds", 0.0)),
            "raw_run_dir": run_source_dir,
            "run_status": metrics.get("run_status", "completed"),
            "error": metrics.get("error", ""),
            "screening_attempt_count": int(metrics.get("screening_attempt_count", 1)),
            "rerun_triggered": bool(metrics.get("rerun_triggered", False)),
            "benchmark_architecture": metrics.get("benchmark_architecture", "batch_orchestrator_v1"),
            "telemetry": _metric_telemetry(metrics),
        })

    metadata = {
        "suite": suite_name,
        "repeats": repeats,
        "review_keys": review_keys,
        "model_presets": model_presets,
        "orchestrator_policy": orchestrator_policy,
        "orchestrator_preset": orchestrator_preset,
        "source_label_policy": source_label_policy,
    }
    return raw_runs, metadata


def _mean_for(rows: list[dict], key: str) -> float | None:
    values = [
        row[key]
        for row in rows
        if row.get(key) is not None
    ]
    if not values:
        return None
    return fmean(values)


def _aggregate_runs(run_metrics: list[dict]) -> list[dict]:
    grouped: dict[tuple[str, str, str, str, str, str, str, str], list[dict]] = {}
    for row in run_metrics:
        key = (
            row.get("benchmark_architecture", "batch_orchestrator_v1"),
            row["gatekeeper_model_label"],
            row["gatekeeper_backend"],
            row["gatekeeper_api_base"],
            row["orchestrator_policy"],
            row["orchestrator_model_label"],
            row["orchestrator_backend"],
            row["orchestrator_api_base"],
        )
        grouped.setdefault(key, []).append(row)

    aggregates: list[dict] = []
    for (
        benchmark_architecture,
        gatekeeper_model_label,
        gatekeeper_backend,
        gatekeeper_api_base,
        orchestrator_policy,
        orchestrator_model_label,
        orchestrator_backend,
        orchestrator_api_base,
    ), rows in grouped.items():
        scored_rows = [row for row in rows if row.get("scored_for_aggregate")]
        aggregates.append({
            "gold_label_policy": rows[0]["gold_label_policy"],
            "benchmark_architecture": benchmark_architecture,
            "gatekeeper_preset": rows[0]["gatekeeper_preset"],
            "gatekeeper_model_label": gatekeeper_model_label,
            "gatekeeper_backend": gatekeeper_backend,
            "gatekeeper_api_base": gatekeeper_api_base,
            "orchestrator_policy": orchestrator_policy,
            "orchestrator_preset": rows[0]["orchestrator_preset"],
            "orchestrator_model_label": orchestrator_model_label,
            "orchestrator_backend": orchestrator_backend,
            "orchestrator_api_base": orchestrator_api_base,
            "n_runs": len(rows),
            "n_scored_runs": len(scored_rows),
            "n_completed_runs": sum(1 for row in rows if row.get("run_status") == "completed"),
            "n_incomplete_runs": sum(1 for row in rows if row.get("run_status") == "incomplete"),
            "n_error_runs": sum(1 for row in rows if row.get("run_status") == "error"),
            "n_unique_reviews": len({row["review_key"] for row in rows}),
            "parse_success_rate": _mean_for(
                [{"value": 1.0 if row.get("parse_success") else 0.0} for row in rows],
                "value",
            ),
            "mean_decision_coverage": _mean_for(rows, "decision_coverage"),
            "mean_accuracy": _mean_for(scored_rows, "accuracy"),
            "mean_precision": _mean_for(scored_rows, "precision"),
            "mean_recall": _mean_for(scored_rows, "recall"),
            "mean_specificity": _mean_for(scored_rows, "specificity"),
            "mean_f1": _mean_for(scored_rows, "f1"),
            "mean_duration_seconds": _mean_for(rows, "duration_seconds"),
            "mean_duration_per_study_seconds": _mean_for(rows, "duration_per_study_seconds"),
            "mean_total_input_tokens": _mean_for(rows, "total_input_tokens"),
            "mean_total_output_tokens": _mean_for(rows, "total_output_tokens"),
            "mean_total_tokens": _mean_for(rows, "total_tokens"),
            "mean_total_steps": _mean_for(rows, "total_steps"),
            "mean_orchestrator_steps": _mean_for(rows, "orchestrator_step_count"),
            "mean_gatekeeper_steps": _mean_for(rows, "gatekeeper_step_count"),
            "mean_error_steps": _mean_for(rows, "error_step_count"),
            "mean_retry_count": _mean_for(rows, "retry_count"),
            "mean_resume_count": _mean_for(rows, "resume_count"),
            "mean_empty_rationale_count": _mean_for(rows, "empty_rationale_count"),
            "mean_duplicate_rationale_count": _mean_for(rows, "duplicate_rationale_count"),
            "mean_rationale_reuse_rate": _mean_for(rows, "rationale_reuse_rate"),
        })

    aggregates.sort(
        key=lambda row: (
            row["mean_f1"] is not None,
            row["mean_f1"] or -1.0,
            row["mean_recall"] or -1.0,
            row["mean_accuracy"] or -1.0,
        ),
        reverse=True,
    )
    return aggregates


def _aggregate_runs_by_review(run_metrics: list[dict]) -> list[dict]:
    grouped: dict[tuple[str, str, str, int, int, int, str, str, str, str, str, str, str], list[dict]] = {}
    for row in run_metrics:
        key = (
            row["review_key"],
            row["review_title"],
            row["review_url"],
            row["n_studies"],
            row["gold_pass_count"],
            row["gold_exclude_count"],
            row.get("benchmark_architecture", "batch_orchestrator_v1"),
            row["gatekeeper_model_label"],
            row["gatekeeper_backend"],
            row["gatekeeper_api_base"],
            row["orchestrator_policy"],
            row["orchestrator_model_label"],
            row["orchestrator_api_base"],
        )
        grouped.setdefault(key, []).append(row)

    aggregates: list[dict] = []
    for (
        review_key,
        review_title,
        review_url,
        n_studies,
        gold_pass_count,
        gold_exclude_count,
        benchmark_architecture,
        gatekeeper_model_label,
        gatekeeper_backend,
        gatekeeper_api_base,
        orchestrator_policy,
        orchestrator_model_label,
        orchestrator_api_base,
    ), rows in grouped.items():
        scored_rows = [row for row in rows if row.get("scored_for_aggregate")]
        aggregates.append({
            "gold_label_policy": rows[0]["gold_label_policy"],
            "benchmark_architecture": benchmark_architecture,
            "review_key": review_key,
            "review_title": review_title,
            "review_url": review_url,
            "split": rows[0]["split"],
            "n_studies": n_studies,
            "gold_pass_count": gold_pass_count,
            "gold_exclude_count": gold_exclude_count,
            "gatekeeper_preset": rows[0]["gatekeeper_preset"],
            "gatekeeper_model_label": gatekeeper_model_label,
            "gatekeeper_backend": gatekeeper_backend,
            "gatekeeper_api_base": gatekeeper_api_base,
            "orchestrator_policy": orchestrator_policy,
            "orchestrator_preset": rows[0]["orchestrator_preset"],
            "orchestrator_model_label": orchestrator_model_label,
            "orchestrator_backend": rows[0]["orchestrator_backend"],
            "orchestrator_api_base": orchestrator_api_base,
            "n_runs": len(rows),
            "n_scored_runs": len(scored_rows),
            "n_completed_runs": sum(1 for row in rows if row.get("run_status") == "completed"),
            "n_incomplete_runs": sum(1 for row in rows if row.get("run_status") == "incomplete"),
            "n_error_runs": sum(1 for row in rows if row.get("run_status") == "error"),
            "parse_success_rate": _mean_for(
                [{"value": 1.0 if row.get("parse_success") else 0.0} for row in rows],
                "value",
            ),
            "mean_decision_coverage": _mean_for(rows, "decision_coverage"),
            "mean_accuracy": _mean_for(scored_rows, "accuracy"),
            "mean_precision": _mean_for(scored_rows, "precision"),
            "mean_recall": _mean_for(scored_rows, "recall"),
            "mean_specificity": _mean_for(scored_rows, "specificity"),
            "mean_f1": _mean_for(scored_rows, "f1"),
            "mean_duration_seconds": _mean_for(rows, "duration_seconds"),
            "mean_duration_per_study_seconds": _mean_for(rows, "duration_per_study_seconds"),
            "mean_total_tokens": _mean_for(rows, "total_tokens"),
            "mean_total_steps": _mean_for(rows, "total_steps"),
            "mean_error_steps": _mean_for(rows, "error_step_count"),
            "mean_retry_count": _mean_for(rows, "retry_count"),
            "mean_resume_count": _mean_for(rows, "resume_count"),
            "mean_empty_rationale_count": _mean_for(rows, "empty_rationale_count"),
            "mean_duplicate_rationale_count": _mean_for(rows, "duplicate_rationale_count"),
            "mean_rationale_reuse_rate": _mean_for(rows, "rationale_reuse_rate"),
        })

    aggregates.sort(
        key=lambda row: (
            row["n_studies"],
            row["review_title"].lower(),
            -(row["mean_f1"] or -1.0),
            -(row["mean_recall"] or -1.0),
            -(row["mean_accuracy"] or -1.0),
        )
    )
    return aggregates


def _format_metric(value: float | None) -> str:
    return "n/a" if value is None else f"{value:.3f}"


def _write_summary_json(
    experiment_dir: Path,
    *,
    suite_name: str,
    repeats: int,
    review_keys: list[str],
    model_presets: list[str],
    orchestrator_policy: str,
    orchestrator_preset: str,
    gold_label_policy: str,
    run_metrics: list[dict],
    aggregates: list[dict],
    review_aggregates: list[dict],
) -> dict:
    summary = {
        "generated_at": datetime.now().isoformat(),
        "suite": suite_name,
        "repeats": repeats,
        "review_keys": review_keys,
        "model_presets": model_presets,
        "orchestrator_policy": orchestrator_policy,
        "orchestrator_preset": orchestrator_preset,
        "gold_label_policy": gold_label_policy,
        "runs": run_metrics,
        "leaderboard": aggregates,
        "review_leaderboard": review_aggregates,
    }
    def _write(path: Path) -> None:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)

    _atomic_write(experiment_dir / "summary.json", _write)
    return summary


def _write_summary_csv(experiment_dir: Path, run_metrics: list[dict]) -> None:
    if not run_metrics:
        return
    seen = set()
    fieldnames: list[str] = []
    for field in _SUMMARY_CSV_PRIORITY_FIELDS:
        if any(field in row for row in run_metrics) and field not in seen:
            fieldnames.append(field)
            seen.add(field)
    for row in run_metrics:
        for field in row:
            if field not in seen:
                fieldnames.append(field)
                seen.add(field)
    def _write(path: Path) -> None:
        with open(path, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(run_metrics)

    _atomic_write(experiment_dir / "summary.csv", _write)


def _write_leaderboard_markdown(experiment_dir: Path, aggregates: list[dict]) -> None:
    lines = [
        "# Screening Benchmark Leaderboard",
        "",
        (
            f"Gold label policy: "
            f"`{aggregates[0]['gold_label_policy']}`"
            if aggregates
            else "Gold label policy: n/a"
        ),
        "",
        "Metrics are averaged only over scored runs with complete per-study decision coverage.",
        "",
        "| Rank | Architecture | Gatekeeper Model | Orchestrator Policy | Orchestrator Model | Runs | Scored | Incomplete | Errors | F1 | Recall | Precision | Accuracy | Specificity | Parse Success | Coverage |",
        "|------|--------------|------------------|---------------------|--------------------|------|--------|------------|--------|----|--------|-----------|----------|-------------|---------------|----------|",
    ]

    for rank, row in enumerate(aggregates, start=1):
        lines.append(
            "| {rank} | {architecture} | {gatekeeper} | {policy} | {orchestrator} | {runs} | {scored} | {incomplete} | {errors} | {f1} | {recall} | {precision} | {accuracy} | {specificity} | {parse_success} | {coverage} |".format(
                rank=rank,
                architecture=row.get("benchmark_architecture", "batch_orchestrator_v1"),
                gatekeeper=row["gatekeeper_model_label"],
                policy=row["orchestrator_policy"],
                orchestrator=row["orchestrator_model_label"],
                runs=row["n_runs"],
                scored=row["n_scored_runs"],
                incomplete=row["n_incomplete_runs"],
                errors=row["n_error_runs"],
                f1=_format_metric(row["mean_f1"]),
                recall=_format_metric(row["mean_recall"]),
                precision=_format_metric(row["mean_precision"]),
                accuracy=_format_metric(row["mean_accuracy"]),
                specificity=_format_metric(row["mean_specificity"]),
                parse_success=_format_metric(row["parse_success_rate"]),
                coverage=_format_metric(row["mean_decision_coverage"]),
            )
        )

    def _write(path: Path) -> None:
        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")

    _atomic_write(experiment_dir / "leaderboard.md", _write)


def _write_review_leaderboard_markdown(
    experiment_dir: Path,
    review_aggregates: list[dict],
) -> None:
    lines = [
        "# Review-Level Screening Benchmark Leaderboard",
        "",
        "This file compares model configurations within each review.",
        "",
        (
            f"Gold label policy: "
            f"`{review_aggregates[0]['gold_label_policy']}`"
            if review_aggregates
            else "Gold label policy: n/a"
        ),
    ]

    if not review_aggregates:
        lines.extend(["", "No benchmark runs were recorded."])
    else:
        grouped: dict[tuple[str, str, str, int, int, int], list[dict]] = {}
        for row in review_aggregates:
            key = (
                row["review_key"],
                row["review_title"],
                row["review_url"],
                row["n_studies"],
                row["gold_pass_count"],
                row["gold_exclude_count"],
            )
            grouped.setdefault(key, []).append(row)

        for (
            review_key,
            review_title,
            review_url,
            n_studies,
            gold_pass_count,
            gold_exclude_count,
        ), rows in grouped.items():
            sorted_rows = sorted(
                rows,
                key=lambda row: (
                    row["mean_f1"] is not None,
                    row["mean_f1"] or -1.0,
                    row["mean_recall"] or -1.0,
                    row["mean_accuracy"] or -1.0,
                ),
                reverse=True,
            )
            lines.extend([
                "",
                f"## {review_key}",
                "",
                f"**Title:** {review_title}",
                f"**URL:** {review_url}",
                (
                    f"**Studies:** {n_studies} | **Gold pass:** {gold_pass_count} | "
                    f"**Gold exclude:** {gold_exclude_count}"
                ),
                "",
                "Metrics below are averaged only over scored runs with complete per-study decision coverage.",
                "",
                "| Rank | Architecture | Gatekeeper Model | Orchestrator Policy | Orchestrator Model | Runs | Scored | Incomplete | Errors | F1 | Recall | Precision | Accuracy | Specificity | Parse Success | Coverage |",
                "|------|--------------|------------------|---------------------|--------------------|------|--------|------------|--------|----|--------|-----------|----------|-------------|---------------|----------|",
            ])
            for rank, row in enumerate(sorted_rows, start=1):
                lines.append(
                    "| {rank} | {architecture} | {gatekeeper} | {policy} | {orchestrator} | {runs} | {scored} | {incomplete} | {errors} | {f1} | {recall} | {precision} | {accuracy} | {specificity} | {parse_success} | {coverage} |".format(
                        rank=rank,
                        architecture=row.get("benchmark_architecture", "batch_orchestrator_v1"),
                        gatekeeper=row["gatekeeper_model_label"],
                        policy=row["orchestrator_policy"],
                        orchestrator=row["orchestrator_model_label"],
                        runs=row["n_runs"],
                        scored=row["n_scored_runs"],
                        incomplete=row["n_incomplete_runs"],
                        errors=row["n_error_runs"],
                        f1=_format_metric(row["mean_f1"]),
                        recall=_format_metric(row["mean_recall"]),
                        precision=_format_metric(row["mean_precision"]),
                        accuracy=_format_metric(row["mean_accuracy"]),
                        specificity=_format_metric(row["mean_specificity"]),
                        parse_success=_format_metric(row["parse_success_rate"]),
                        coverage=_format_metric(row["mean_decision_coverage"]),
                    )
                )

    def _write(path: Path) -> None:
        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")

    _atomic_write(experiment_dir / "review_leaderboard.md", _write)


# ---------------------------------------------------------------------------
# Experiment-level batch benchmark and reruns
# ---------------------------------------------------------------------------

def rerun_screening_reviews_in_experiment(
    *,
    experiment_dir: Path,
    review_keys: list[str],
    include_subagent_steps: bool = True,
    execute_policy_notebooks: bool = True,
    orchestrator_max_steps: int | None = None,
) -> tuple[Path, dict]:
    """
    Rerun selected reviews inside an existing batch experiment and rematerialize summaries.
    """
    if not review_keys:
        raise ValueError("--reviews is required when using --rerun-in-experiment")

    experiment_dir = Path(experiment_dir)
    checkpoint_path = experiment_dir / "benchmark_checkpoint.json"
    checkpoint = _read_json(checkpoint_path) if checkpoint_path.exists() else None
    if checkpoint:
        checkpoint_architecture = checkpoint.get("benchmark_architecture", "batch_orchestrator_v1")
        if checkpoint_architecture != "batch_orchestrator_v1":
            raise ValueError(
                f"Experiment is not a batch benchmark: {checkpoint_architecture}"
            )

    selected_label_policies = list(SCREENING_LABEL_POLICIES)
    raw_runs, metadata = _load_existing_batch_raw_runs(
        experiment_dir,
        checkpoint=checkpoint,
        selected_label_policies=selected_label_policies,
    )
    suite_name = metadata["suite"]
    original_review_keys = metadata["review_keys"]
    original_model_keys = metadata["model_presets"]
    orchestrator_policy = metadata["orchestrator_policy"]
    orchestrator_preset = metadata["orchestrator_preset"]
    repeats = metadata["repeats"]
    resolved_orchestrator_max_steps = int(
        orchestrator_max_steps
        if orchestrator_max_steps is not None
        else (
            checkpoint.get("orchestrator_max_steps", 20)
            if checkpoint
            else 20
        )
    )

    unknown_review_keys = [key for key in review_keys if key not in original_review_keys]
    if unknown_review_keys:
        raise ValueError(
            "Cannot rerun review key(s) outside the original experiment: "
            + ", ".join(unknown_review_keys)
        )

    raw_runs_by_id = {
        _run_name(
            raw_run["review_case"],
            raw_run["gatekeeper_model"],
            raw_run["orchestrator_policy"],
            raw_run["orchestrator_model"],
            raw_run["run_index"],
        ): raw_run
        for raw_run in raw_runs
    }
    selected_reviews = resolve_review_selection(suite_name, review_keys)
    gatekeeper_models = [get_model_preset(model_key).resolve() for model_key in original_model_keys]
    fixed_orchestrator_model = (
        get_model_preset(orchestrator_preset).resolve()
        if orchestrator_policy == "fixed"
        else None
    )
    raw_runs_output_root = _raw_runs_checkpoint_root(experiment_dir)

    for gatekeeper_model in gatekeeper_models:
        for review_case in selected_reviews:
            for run_index in range(1, repeats + 1):
                orchestrator_model = (
                    fixed_orchestrator_model
                    if orchestrator_policy == "fixed"
                    else gatekeeper_model
                )
                if orchestrator_model is None:
                    raise ValueError("Unable to resolve orchestrator model for rerun.")
                logger.info(
                    "Rerunning batch benchmark review in existing experiment: review=%s gatekeeper=%s orchestrator=%s repeat=%d/%d",
                    review_case.key,
                    gatekeeper_model.key,
                    orchestrator_model.key,
                    run_index,
                    repeats,
                )
                raw_run = run_screening_review(
                    suite_name=suite_name,
                    review_case=review_case,
                    gatekeeper_model=gatekeeper_model,
                    orchestrator_model=orchestrator_model,
                    orchestrator_policy=orchestrator_policy,
                    run_index=run_index,
                    output_root=raw_runs_output_root,
                    label_policy="include_label_0_5",
                    include_subagent_steps=include_subagent_steps,
                    orchestrator_max_steps=resolved_orchestrator_max_steps,
                )
                run_id = _run_name(
                    review_case,
                    gatekeeper_model,
                    orchestrator_policy,
                    orchestrator_model,
                    run_index,
                )
                raw_runs_by_id[run_id] = raw_run

    merged_raw_runs = _sort_raw_runs(
        list(raw_runs_by_id.values()),
        review_keys=original_review_keys,
        model_keys=original_model_keys,
    )
    total_expected_raw_runs = len(original_review_keys) * len(original_model_keys) * repeats
    policy_summaries = _checkpoint_policy_outputs(
        experiment_dir,
        suite_name=suite_name,
        repeats=repeats,
        review_keys=original_review_keys,
        model_presets=original_model_keys,
        orchestrator_policy=orchestrator_policy,
        orchestrator_preset=orchestrator_preset,
        selected_label_policies=selected_label_policies,
        raw_runs=merged_raw_runs,
    )

    for label_policy, output_record in list(policy_summaries.items()):
        policy_dir = Path(output_record["directory"])
        notebook_info = write_policy_eda_notebook(
            policy_dir,
            execute=execute_policy_notebooks,
        )
        html_report_info = write_policy_html_report(policy_dir)
        policy_summaries[label_policy] = _policy_output_record(
            policy_dir,
            output_record["summary"],
            notebook_info=notebook_info,
            html_report_info=html_report_info,
        )

    comparison_report = None
    if {"include_label_0_5", "exclude_label_0_5"}.issubset(policy_summaries):
        comparison_report = write_policy_comparison_report(experiment_dir)["report_path"]

    _write_benchmark_checkpoint(
        experiment_dir,
        suite_name=suite_name,
        benchmark_architecture="batch_orchestrator_v1",
        repeats=repeats,
        review_keys=original_review_keys,
        model_presets=original_model_keys,
        orchestrator_policy=orchestrator_policy,
        orchestrator_preset=orchestrator_preset,
        selected_label_policies=selected_label_policies,
        total_expected_raw_runs=total_expected_raw_runs,
        raw_runs=merged_raw_runs,
        policy_summaries=policy_summaries,
        comparison_report=comparison_report,
        extra_metadata={
            "orchestrator_max_steps": resolved_orchestrator_max_steps,
        },
    )

    return experiment_dir, {
        "generated_at": datetime.now().isoformat(),
        "suite": suite_name,
        "benchmark_architecture": "batch_orchestrator_v1",
        "repeats": repeats,
        "review_keys": original_review_keys,
        "rerun_review_keys": review_keys,
        "model_presets": original_model_keys,
        "orchestrator_policy": orchestrator_policy,
        "orchestrator_preset": orchestrator_preset,
        "orchestrator_max_steps": resolved_orchestrator_max_steps,
        "gold_label_policies": selected_label_policies,
        "raw_runs_dir": str(raw_runs_output_root),
        "checkpoint_manifest": str(experiment_dir / "benchmark_checkpoint.json"),
        "completed_raw_run_count": len(merged_raw_runs),
        "total_expected_raw_runs": total_expected_raw_runs,
        "comparison_html_report": comparison_report,
        "policy_outputs": policy_summaries,
    }


def run_screening_benchmark(
    *,
    suite_name: str = "screening_ladder",
    model_presets: list[str] | None = None,
    repeats: int = 1,
    orchestrator_policy: str = "fixed",
    orchestrator_model_key: str = "openai_gpt5",
    review_keys: list[str] | None = None,
    gold_label_policies: list[str] | None = None,
    include_subagent_steps: bool = True,
    execute_policy_notebooks: bool = True,
    canonical_mode: str = "none",
    orchestrator_max_steps: int = 20,
) -> tuple[Path, dict]:
    """
    Run the Gatekeeper screening benchmark matrix and write experiment summaries.
    """
    if repeats < 1:
        raise ValueError("--repeats must be at least 1")
    if orchestrator_policy not in {"fixed", "match-gatekeeper"}:
        raise ValueError("--orchestrator-policy must be 'fixed' or 'match-gatekeeper'")
    if canonical_mode not in {"auto", "none", "force"}:
        raise ValueError("canonical_mode must be 'auto', 'none', or 'force'")
    selected_label_policies = list(SCREENING_LABEL_POLICIES)

    selected_reviews = resolve_review_selection(suite_name, review_keys)
    resolved_gatekeeper_models = resolve_model_presets(model_presets)
    fixed_orchestrator_model = get_model_preset(orchestrator_model_key).resolve()
    experiment_dir = _experiment_root(suite_name)
    review_key_list = [review.key for review in selected_reviews]
    model_key_list = [model.key for model in resolved_gatekeeper_models]
    orchestrator_preset = (
        fixed_orchestrator_model.key
        if orchestrator_policy == "fixed"
        else "match-gatekeeper"
    )
    raw_runs_output_root = _raw_runs_checkpoint_root(experiment_dir)
    total_expected_raw_runs = (
        len(selected_reviews) * len(resolved_gatekeeper_models) * repeats
    )

    logger.info("Screening benchmark output dir: %s", experiment_dir)
    logger.info(
        "Running suite=%s reviews=%d gatekeeper_models=%d repeats=%d policy=%s",
        suite_name,
        len(selected_reviews),
        len(resolved_gatekeeper_models),
        repeats,
        orchestrator_policy,
    )

    raw_runs: list[dict] = []
    policy_summaries: dict[str, dict] = {}
    comparison_report = None
    for gatekeeper_model in resolved_gatekeeper_models:
        for review_case in selected_reviews:
            for run_index in range(1, repeats + 1):
                orchestrator_model = (
                    fixed_orchestrator_model
                    if orchestrator_policy == "fixed"
                    else gatekeeper_model
                )
                logger.info(
                    "Benchmark run: review=%s gatekeeper=%s orchestrator=%s repeat=%d/%d",
                    review_case.key,
                    gatekeeper_model.key,
                    orchestrator_model.key,
                    run_index,
                    repeats,
                )
                raw_run = run_screening_review(
                    suite_name=suite_name,
                    review_case=review_case,
                    gatekeeper_model=gatekeeper_model,
                    orchestrator_model=orchestrator_model,
                    orchestrator_policy=orchestrator_policy,
                    run_index=run_index,
                    output_root=raw_runs_output_root,
                    label_policy="include_label_0_5",
                    include_subagent_steps=include_subagent_steps,
                    orchestrator_max_steps=orchestrator_max_steps,
                )
                raw_runs.append(raw_run)
                policy_summaries = _checkpoint_policy_outputs(
                    experiment_dir,
                    suite_name=suite_name,
                    repeats=repeats,
                    review_keys=review_key_list,
                    model_presets=model_key_list,
                    orchestrator_policy=orchestrator_policy,
                    orchestrator_preset=orchestrator_preset,
                    selected_label_policies=selected_label_policies,
                    raw_runs=raw_runs,
                )
                _write_benchmark_checkpoint(
                    experiment_dir,
                    suite_name=suite_name,
                    benchmark_architecture="batch_orchestrator_v1",
                    repeats=repeats,
                    review_keys=review_key_list,
                    model_presets=model_key_list,
                    orchestrator_policy=orchestrator_policy,
                    orchestrator_preset=orchestrator_preset,
                    selected_label_policies=selected_label_policies,
                    total_expected_raw_runs=total_expected_raw_runs,
                    raw_runs=raw_runs,
                    policy_summaries=policy_summaries,
                    comparison_report=comparison_report,
                    extra_metadata={
                        "orchestrator_max_steps": orchestrator_max_steps,
                    },
                )
                if canonical_mode != "none":
                    register_canonical_sources_from_experiment(
                        experiment_dir,
                        mode=canonical_mode,
                    )

    for label_policy, output_record in list(policy_summaries.items()):
        policy_dir = Path(output_record["directory"])
        notebook_info = write_policy_eda_notebook(
            policy_dir,
            execute=execute_policy_notebooks,
        )
        html_report_info = write_policy_html_report(policy_dir)
        policy_summaries[label_policy] = _policy_output_record(
            policy_dir,
            output_record["summary"],
            notebook_info=notebook_info,
            html_report_info=html_report_info,
        )

    if {"include_label_0_5", "exclude_label_0_5"}.issubset(policy_summaries):
        comparison_report = write_policy_comparison_report(experiment_dir)["report_path"]

    _write_benchmark_checkpoint(
        experiment_dir,
        suite_name=suite_name,
        benchmark_architecture="batch_orchestrator_v1",
        repeats=repeats,
        review_keys=review_key_list,
        model_presets=model_key_list,
        orchestrator_policy=orchestrator_policy,
        orchestrator_preset=orchestrator_preset,
        selected_label_policies=selected_label_policies,
        total_expected_raw_runs=total_expected_raw_runs,
        raw_runs=raw_runs,
        policy_summaries=policy_summaries,
        comparison_report=comparison_report,
        extra_metadata={
            "orchestrator_max_steps": orchestrator_max_steps,
        },
    )

    return experiment_dir, {
        "generated_at": datetime.now().isoformat(),
        "suite": suite_name,
        "repeats": repeats,
        "review_keys": review_key_list,
        "model_presets": model_key_list,
        "orchestrator_policy": orchestrator_policy,
        "orchestrator_preset": orchestrator_preset,
        "orchestrator_max_steps": orchestrator_max_steps,
        "gold_label_policies": selected_label_policies,
        "raw_runs_dir": str(raw_runs_output_root),
        "checkpoint_manifest": str(experiment_dir / "benchmark_checkpoint.json"),
        "completed_raw_run_count": len(raw_runs),
        "total_expected_raw_runs": total_expected_raw_runs,
        "comparison_html_report": comparison_report,
        "policy_outputs": policy_summaries,
    }
