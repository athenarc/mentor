"""
Utilities for backfilling older screening benchmark directories.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path

from bastirr.benchmarking.comparison_reports import write_policy_comparison_report
from bastirr.benchmarking.html_reports import write_policy_html_report
from bastirr.benchmarking.metrics import SCREENING_LABEL_POLICIES
from bastirr.benchmarking.model_presets import get_model_preset
from bastirr.benchmarking.notebooks import write_policy_eda_notebook
from bastirr.benchmarking.review_suites import resolve_review_selection
from bastirr.benchmarking.runner import (
    _materialize_policy_outputs,
    _policy_output_record,
    _write_benchmark_checkpoint,
)
from bastirr.config import OUTPUT_DIR
from bastirr.data import load_review


_POLICY_DIR_NAMES = {
    "include_label_0_5": "include_policy",
    "exclude_label_0_5": "exclude_policy",
}
_REVIEW_CACHE: dict[tuple[str, str], object] = {}


def _policy_dir_name(label_policy: str) -> str:
    return _POLICY_DIR_NAMES.get(label_policy, label_policy)


def _remove_path(path: Path) -> None:
    if not path.exists() and not path.is_symlink():
        return
    if path.is_dir() and not path.is_symlink():
        shutil.rmtree(path)
    else:
        path.unlink()


def _read_screening_decisions(evidence_path: Path) -> list[dict]:
    if not evidence_path.exists():
        return []
    with open(evidence_path, "r", encoding="utf-8") as f:
        payload = json.load(f)
    decisions = payload.get("screening_decisions", [])
    return decisions if isinstance(decisions, list) else []


def _load_review_cached(review_url: str, split: str):
    cache_key = (review_url, split)
    if cache_key not in _REVIEW_CACHE:
        _REVIEW_CACHE[cache_key] = load_review(review_url, split)
    return _REVIEW_CACHE[cache_key]


def _resolve_existing_path(path_value: str | Path) -> Path:
    path = Path(path_value)
    if path.exists():
        return path
    if path.is_absolute():
        parts = path.parts
        for index in range(len(parts) - 2):
            if parts[index:index + 3] == ("bastirr", "output", "screening_benchmarks"):
                candidate = Path(*parts[index:])
                if candidate.exists():
                    return candidate
    return path


def _metric_telemetry(metrics: dict) -> dict:
    return {
        key: metrics[key]
        for key in (
            "total_input_tokens",
            "total_output_tokens",
            "total_tokens",
            "total_steps",
            "action_step_count",
            "planning_step_count",
            "error_step_count",
            "retry_count",
            "resume_count",
            "duration_per_study_seconds",
            "agent_step_counts",
            "agent_input_tokens",
            "agent_output_tokens",
            "agent_duration_seconds",
            "orchestrator_step_count",
            "gatekeeper_step_count",
            "orchestrator_input_tokens",
            "orchestrator_output_tokens",
            "gatekeeper_input_tokens",
            "gatekeeper_output_tokens",
            "chunk_count",
            "chunk_sizes",
        )
        if key in metrics
    }


def _load_existing_policy_record(experiment_dir: Path, label_policy: str) -> dict | None:
    policy_dir = experiment_dir / _policy_dir_name(label_policy)
    summary_path = policy_dir / "summary.json"
    if not summary_path.exists():
        return None
    with open(summary_path, "r", encoding="utf-8") as f:
        summary = json.load(f)
    notebook_path = policy_dir / "screening_results_analysis.ipynb"
    html_path = policy_dir / "screening_results_summary.html"
    return _policy_output_record(
        policy_dir,
        summary,
        notebook_info={
            "notebook_path": str(notebook_path) if notebook_path.exists() else "",
            "executed": False,
            "execution_error": "",
        },
        html_report_info={
            "report_path": str(html_path) if html_path.exists() else "",
        },
    )


def _raw_run_source_from_checkpoint(
    experiment_dir: Path,
    checkpoint_run: dict,
    *,
    selected_label_policies: list[str],
) -> Path:
    raw_run_dir = checkpoint_run.get("raw_run_dir")
    if raw_run_dir:
        resolved = _resolve_existing_path(raw_run_dir)
        if (resolved / "evidence.json").exists() and (resolved / "metrics.json").exists():
            return resolved

    run_id = checkpoint_run["benchmark_run_id"]
    for label_policy in selected_label_policies:
        candidate = experiment_dir / _policy_dir_name(label_policy) / "runs" / run_id
        if (candidate / "evidence.json").exists() and (candidate / "metrics.json").exists():
            return candidate

    for policy_dir in sorted(experiment_dir.glob("*_policy")):
        candidate = policy_dir / "runs" / run_id
        if (candidate / "evidence.json").exists() and (candidate / "metrics.json").exists():
            return candidate

    raise FileNotFoundError(
        f"Could not find raw or policy run artifacts for checkpoint run '{run_id}' "
        f"under {experiment_dir}."
    )


def _load_checkpoint_raw_runs(
    experiment_dir: Path,
    *,
    checkpoint: dict,
    selected_label_policies: list[str],
) -> list[dict]:
    suite_name = checkpoint["suite"]
    review_case_by_key = {
        review.key: review
        for review in resolve_review_selection(suite_name, checkpoint.get("review_keys") or None)
    }

    raw_runs: list[dict] = []
    for checkpoint_run in checkpoint.get("completed_runs", []):
        run_source_dir = _raw_run_source_from_checkpoint(
            experiment_dir,
            checkpoint_run,
            selected_label_policies=selected_label_policies,
        )
        metrics_path = run_source_dir / "metrics.json"
        evidence_path = run_source_dir / "evidence.json"
        with open(metrics_path, "r", encoding="utf-8") as f:
            metrics = json.load(f)

        review_key = checkpoint_run.get("review_key") or metrics["review_key"]
        review_case = review_case_by_key.get(review_key)
        if review_case is None:
            raise ValueError(
                f"Run '{checkpoint_run.get('benchmark_run_id', run_source_dir.name)}' "
                f"references review '{review_key}', which was not found in suite '{suite_name}'."
            )

        review = _load_review_cached(review_case.review_url, review_case.split)
        if review is None:
            raise ValueError(
                f"Unable to load review '{review_case.review_url}' from split "
                f"'{review_case.split}' while backfilling '{experiment_dir.name}'."
            )

        raw_runs.append({
            "suite_name": suite_name,
            "review_case": review_case,
            "review": review,
            "screening_decisions": _read_screening_decisions(evidence_path),
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
            "benchmark_architecture": metrics.get(
                "benchmark_architecture",
                checkpoint.get("benchmark_architecture", "batch_orchestrator_v1"),
            ),
            "telemetry": _metric_telemetry(metrics),
        })
    return raw_runs


def _sort_raw_runs(raw_runs: list[dict], *, review_keys: list[str], model_keys: list[str]) -> list[dict]:
    review_order = {key: index for index, key in enumerate(review_keys)}
    model_order = {key: index for index, key in enumerate(model_keys)}
    return sorted(
        raw_runs,
        key=lambda raw_run: (
            model_order.get(raw_run["gatekeeper_model"].key, len(model_order)),
            review_order.get(raw_run["review_case"].key, len(review_order)),
            raw_run["run_index"],
        ),
    )


def _backfill_checkpoint_policy_views(
    experiment_dir: Path,
    *,
    checkpoint: dict,
    label_policies: list[str] | None,
    overwrite_existing_policies: bool,
    execute_policy_notebooks: bool,
) -> dict:
    suite_name = checkpoint["suite"]
    repeats = int(checkpoint.get("repeats", 1))
    review_keys = checkpoint.get("review_keys") or []
    model_presets = checkpoint.get("model_presets") or []
    orchestrator_policy = checkpoint["orchestrator_policy"]
    orchestrator_preset = checkpoint["orchestrator_preset"]
    selected_label_policies = label_policies or list(SCREENING_LABEL_POLICIES)
    raw_runs = _sort_raw_runs(
        _load_checkpoint_raw_runs(
            experiment_dir,
            checkpoint=checkpoint,
            selected_label_policies=selected_label_policies,
        ),
        review_keys=review_keys,
        model_keys=model_presets,
    )

    policy_outputs: dict[str, dict] = {}
    materialized_policies: list[str] = []
    skipped_existing_policies: list[str] = []
    for label_policy in selected_label_policies:
        existing_record = _load_existing_policy_record(experiment_dir, label_policy)
        if existing_record and not overwrite_existing_policies:
            policy_outputs[label_policy] = existing_record
            skipped_existing_policies.append(label_policy)
            continue

        policy_dir = experiment_dir / _policy_dir_name(label_policy)
        _remove_path(policy_dir)
        policy_dir, policy_summary = _materialize_policy_outputs(
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
        notebook_info = write_policy_eda_notebook(
            policy_dir,
            execute=execute_policy_notebooks,
        )
        html_report_info = write_policy_html_report(policy_dir)
        policy_outputs[label_policy] = _policy_output_record(
            policy_dir,
            policy_summary,
            notebook_info=notebook_info,
            html_report_info=html_report_info,
        )
        materialized_policies.append(label_policy)

    comparison_report = checkpoint.get("comparison_html_report")
    if {"include_label_0_5", "exclude_label_0_5"}.issubset(policy_outputs):
        comparison_report = write_policy_comparison_report(experiment_dir)["report_path"]

    _write_benchmark_checkpoint(
        experiment_dir,
        suite_name=suite_name,
        benchmark_architecture=checkpoint.get("benchmark_architecture", "batch_orchestrator_v1"),
        repeats=repeats,
        review_keys=review_keys,
        model_presets=model_presets,
        orchestrator_policy=orchestrator_policy,
        orchestrator_preset=orchestrator_preset,
        selected_label_policies=selected_label_policies,
        total_expected_raw_runs=int(checkpoint.get("total_expected_raw_runs") or len(raw_runs)),
        raw_runs=raw_runs,
        policy_summaries=policy_outputs,
        comparison_report=comparison_report,
        extra_metadata={
            key: checkpoint[key]
            for key in ("loop_mode", "chunk_count", "chunk_size")
            if key in checkpoint
        },
    )

    return {
        "experiment_dir": str(experiment_dir),
        "comparison_html_report": comparison_report,
        "policies": policy_outputs,
        "materialized_policies": materialized_policies,
        "skipped_existing_policies": skipped_existing_policies,
    }


def backfill_policy_views(
    experiment_dir: Path,
    *,
    label_policies: list[str] | None = None,
    remove_flat_outputs: bool = True,
    remove_shared_runs: bool = True,
    execute_policy_notebooks: bool = True,
    overwrite_existing_policies: bool = False,
) -> dict:
    """
    Backfill an older flat screening benchmark directory into policy subfolders.

    Reuses the existing shared raw run artifacts under ``runs/`` and derives
    separate ``include_policy/`` and ``exclude_policy/`` views without rerunning
    the models.
    """
    experiment_dir = Path(experiment_dir)
    checkpoint_path = experiment_dir / "benchmark_checkpoint.json"
    if checkpoint_path.exists():
        with open(checkpoint_path, "r", encoding="utf-8") as f:
            checkpoint = json.load(f)
        return _backfill_checkpoint_policy_views(
            experiment_dir,
            checkpoint=checkpoint,
            label_policies=label_policies,
            overwrite_existing_policies=overwrite_existing_policies,
            execute_policy_notebooks=execute_policy_notebooks,
        )

    summary_path = experiment_dir / "summary.json"
    runs_dir = experiment_dir / "runs"

    if not summary_path.exists():
        raise FileNotFoundError(f"Expected summary.json at: {summary_path}")
    if not runs_dir.exists():
        raise FileNotFoundError(f"Expected shared runs directory at: {runs_dir}")

    with open(summary_path, "r", encoding="utf-8") as f:
        summary = json.load(f)

    suite_name = summary["suite"]
    repeats = int(summary["repeats"])
    review_keys = summary.get("review_keys") or []
    model_presets = summary.get("model_presets") or []
    orchestrator_policy = summary["orchestrator_policy"]
    orchestrator_preset = summary["orchestrator_preset"]
    selected_label_policies = label_policies or list(SCREENING_LABEL_POLICIES)

    review_case_by_key = {
        review.key: review
        for review in resolve_review_selection(suite_name, review_keys or None)
    }

    raw_runs: list[dict] = []
    for run_dir in sorted(path for path in runs_dir.iterdir() if path.is_dir()):
        metrics_path = run_dir / "metrics.json"
        evidence_path = run_dir / "evidence.json"
        if not metrics_path.exists():
            raise FileNotFoundError(f"Expected metrics.json at: {metrics_path}")
        if not evidence_path.exists():
            raise FileNotFoundError(f"Expected evidence.json at: {evidence_path}")

        with open(metrics_path, "r", encoding="utf-8") as f:
            metrics = json.load(f)

        review_key = metrics["review_key"]
        review_case = review_case_by_key.get(review_key)
        if review_case is None:
            raise ValueError(
                f"Run '{run_dir.name}' references review '{review_key}', which was not "
                f"found in suite '{suite_name}'."
            )

        review = _load_review_cached(review_case.review_url, review_case.split)
        if review is None:
            raise ValueError(
                f"Unable to load review '{review_case.review_url}' from split "
                f"'{review_case.split}' while backfilling '{experiment_dir.name}'."
            )

        raw_runs.append({
            "suite_name": suite_name,
            "review_case": review_case,
            "review": review,
            "screening_decisions": _read_screening_decisions(evidence_path),
            "gatekeeper_model": get_model_preset(metrics["gatekeeper_preset"]).resolve(),
            "orchestrator_model": get_model_preset(metrics["orchestrator_preset"]).resolve(),
            "orchestrator_policy": metrics["orchestrator_policy"],
            "run_index": int(metrics["run_index"]),
            "duration_seconds": float(metrics.get("duration_seconds", 0.0)),
            "raw_run_dir": run_dir,
            "run_status": metrics.get("run_status", "completed"),
            "error": metrics.get("error", ""),
            "screening_attempt_count": int(metrics.get("screening_attempt_count", 1)),
            "rerun_triggered": bool(metrics.get("rerun_triggered", False)),
            "benchmark_architecture": metrics.get("benchmark_architecture", "batch_orchestrator_v1"),
            "telemetry": {
                key: metrics[key]
                for key in (
                    "total_input_tokens",
                    "total_output_tokens",
                    "total_tokens",
                    "total_steps",
                    "action_step_count",
                    "planning_step_count",
                    "error_step_count",
                    "retry_count",
                    "resume_count",
                    "duration_per_study_seconds",
                    "agent_step_counts",
                    "agent_input_tokens",
                    "agent_output_tokens",
                    "agent_duration_seconds",
                    "orchestrator_step_count",
                    "gatekeeper_step_count",
                    "orchestrator_input_tokens",
                    "orchestrator_output_tokens",
                    "gatekeeper_input_tokens",
                    "gatekeeper_output_tokens",
                )
                if key in metrics
            },
        })

    policy_outputs: dict[str, dict] = {}
    for label_policy in selected_label_policies:
        policy_dir = experiment_dir / _policy_dir_name(label_policy)
        _remove_path(policy_dir)
        policy_dir, policy_summary = _materialize_policy_outputs(
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
        notebook_info = write_policy_eda_notebook(
            policy_dir,
            execute=execute_policy_notebooks,
        )
        html_report_info = write_policy_html_report(policy_dir)
        policy_outputs[label_policy] = {
            "directory": str(policy_dir),
            "summary_json": str(policy_dir / "summary.json"),
            "summary_csv": str(policy_dir / "summary.csv"),
            "leaderboard_markdown": str(policy_dir / "leaderboard.md"),
            "review_leaderboard_markdown": str(policy_dir / "review_leaderboard.md"),
            "html_report": html_report_info["report_path"],
            "eda_notebook": notebook_info["notebook_path"],
            "eda_notebook_executed": notebook_info["executed"],
            "eda_notebook_execution_error": notebook_info["execution_error"],
            "summary": policy_summary,
        }

    comparison_report = None
    if {"include_label_0_5", "exclude_label_0_5"}.issubset(policy_outputs):
        comparison_report = write_policy_comparison_report(experiment_dir)["report_path"]

    if remove_shared_runs:
        _remove_path(runs_dir)

    if remove_flat_outputs:
        for filename in ("summary.json", "summary.csv", "leaderboard.md", "review_leaderboard.md"):
            _remove_path(experiment_dir / filename)

    return {
        "experiment_dir": str(experiment_dir),
        "comparison_html_report": comparison_report,
        "policies": policy_outputs,
        "materialized_policies": selected_label_policies,
        "skipped_existing_policies": [],
    }


def _needs_policy_backfill(experiment_dir: Path, *, label_policies: list[str]) -> bool:
    checkpoint_path = experiment_dir / "benchmark_checkpoint.json"
    if not checkpoint_path.exists():
        return False
    for label_policy in label_policies:
        policy_dir = experiment_dir / _policy_dir_name(label_policy)
        if not (policy_dir / "summary.json").exists():
            return True
    if {"include_label_0_5", "exclude_label_0_5"}.issubset(label_policies):
        if not (experiment_dir / "screening_policy_comparison.html").exists():
            return True
    return False


def backfill_missing_policy_views(
    *,
    output_root: Path | None = None,
    label_policies: list[str] | None = None,
    execute_policy_notebooks: bool = True,
    overwrite_existing_policies: bool = False,
) -> dict:
    """
    Backfill missing per-policy outputs for checkpointed screening experiments.

    This scans one benchmark output root and reconstructs missing policy folders
    from existing raw or policy run artifacts without rerunning models.
    """
    output_root = Path(output_root or (OUTPUT_DIR / "screening_benchmarks"))
    selected_label_policies = label_policies or list(SCREENING_LABEL_POLICIES)
    experiments = [
        path
        for path in sorted(output_root.iterdir())
        if path.is_dir()
        and not path.name.startswith("_")
        and path.name not in {"totals", "totals_loc"}
        and (
            overwrite_existing_policies
            or _needs_policy_backfill(path, label_policies=selected_label_policies)
        )
    ]
    results = []
    errors = []
    for experiment_dir in experiments:
        try:
            results.append(
                backfill_policy_views(
                    experiment_dir,
                    label_policies=selected_label_policies,
                    remove_flat_outputs=False,
                    remove_shared_runs=False,
                    execute_policy_notebooks=execute_policy_notebooks,
                    overwrite_existing_policies=overwrite_existing_policies,
                )
            )
        except Exception as exc:
            errors.append({
                "experiment_dir": str(experiment_dir),
                "error": f"{type(exc).__name__}: {exc}",
            })
    return {
        "output_root": str(output_root),
        "label_policies": selected_label_policies,
        "scanned_experiments": len([
            path
            for path in output_root.iterdir()
            if path.is_dir()
            and not path.name.startswith("_")
            and path.name not in {"totals", "totals_loc"}
            and (path / "benchmark_checkpoint.json").exists()
        ]),
        "backfilled_experiments": len(results),
        "errors": errors,
        "results": results,
    }
