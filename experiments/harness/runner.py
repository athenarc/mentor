"""
Screening benchmark artifact helpers (materialize, aggregate, checkpoint).

Execution lives in ``experiments.suites.runner``. Post-run scoring lives in
``experiments.harness.analysis``.
"""

from __future__ import annotations

import csv
import json
import logging
import os
import shutil
from datetime import datetime
from pathlib import Path
from statistics import fmean

from experiments.harness.common import (
    metric_telemetry as _metric_telemetry,
    policy_dir_name as _policy_dir_name,
    read_json as _read_json,
)
from experiments.harness.inspection import write_screening_inspection_artifacts
from experiments.harness.metrics import compute_screening_metrics
from experiments.catalog import ResolvedModel
from experiments.suites.review_suites import ScreeningBenchmarkReview
from experiments.harness.telemetry import compute_rationale_metrics

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
)
logger = logging.getLogger("experiments.harness")


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
    gatekeeper_model: ResolvedModel,
    orchestrator_policy: str,
    orchestrator_model: ResolvedModel,
    run_index: int,
) -> str:
    return "_".join([
        review_case.path_slug,
        gatekeeper_model.key,
        orchestrator_policy,
        orchestrator_model.key,
        f"run{run_index}",
    ])


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


def _build_run_metrics(
    *,
    review_case: ScreeningBenchmarkReview,
    review,
    screening_decisions: list[dict],
    gatekeeper_model: ResolvedModel,
    orchestrator_model: ResolvedModel,
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

