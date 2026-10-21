"""
Utilities for backfilling older screening benchmark directories.
"""

from __future__ import annotations

import json
import re
import shutil
from pathlib import Path

from experiments.harness.common import (
    metric_telemetry as _metric_telemetry,
    policy_dir_name as _policy_dir_name,
    resolve_existing_path as _resolve_existing_path,
    sort_raw_runs as _sort_raw_runs,
)
from experiments.harness.comparison_reports import write_policy_comparison_report
from experiments.harness.html_reports import write_policy_html_report
from experiments.harness.metrics import SCREENING_LABEL_POLICIES, compute_screening_metrics
from experiments.catalog import resolve_model
from experiments.harness.notebooks import write_policy_eda_notebook
from experiments.suites.review_suites import resolve_review_selection
from experiments.harness.runner import (
    _materialize_policy_outputs,
    _policy_output_record,
    _write_benchmark_checkpoint,
)
from experiments.paths import OUTPUT_DIR
from experiments.dataset import load_review

_OPTIONAL_TRACE_FILENAMES = ("workflow.log", "activity.md", "screening_progress.json")
_REVIEW_CACHE: dict[tuple[str, str], object] = {}


def _remove_path(path: Path) -> None:
    if not path.exists() and not path.is_symlink():
        return
    if path.is_dir() and not path.is_symlink():
        shutil.rmtree(path)
    else:
        path.unlink()


def _snapshot_policy_trace_files(policy_dir: Path) -> dict[str, dict[str, bytes]]:
    runs_dir = policy_dir / "runs"
    if not runs_dir.exists():
        return {}
    snapshots: dict[str, dict[str, bytes]] = {}
    for run_dir in sorted(path for path in runs_dir.iterdir() if path.is_dir()):
        files = {
            filename: (run_dir / filename).read_bytes()
            for filename in _OPTIONAL_TRACE_FILENAMES
            if (run_dir / filename).is_file()
        }
        if files:
            snapshots[run_dir.name] = files
    return snapshots


def _restore_missing_policy_trace_files(
    policy_dir: Path,
    snapshots: dict[str, dict[str, bytes]],
) -> None:
    for run_name, files in snapshots.items():
        run_dir = policy_dir / "runs" / run_name
        if not run_dir.exists():
            continue
        for filename, content in files.items():
            target = run_dir / filename
            if not target.exists():
                target.write_bytes(content)


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
    raw_runs_root = experiment_dir / "_raw_runs"
    if raw_runs_root.exists():
        matching_raw_dirs = []
        for candidate in sorted(path for path in raw_runs_root.iterdir() if path.is_dir()):
            metrics_path = candidate / "metrics.json"
            evidence_path = candidate / "evidence.json"
            if not evidence_path.exists():
                continue
            if metrics_path.exists():
                with open(metrics_path, "r", encoding="utf-8") as f:
                    metrics = json.load(f)
                if (
                    metrics.get("review_key") == checkpoint_run.get("review_key")
                    and metrics.get("gatekeeper_preset") == checkpoint_run.get("gatekeeper_preset")
                    and metrics.get("orchestrator_policy") == checkpoint_run.get("orchestrator_policy")
                    and metrics.get("orchestrator_preset") == checkpoint_run.get("orchestrator_preset")
                    and int(metrics.get("run_index") or 1) == int(checkpoint_run.get("run_index") or 1)
                ):
                    matching_raw_dirs.append(candidate)
            elif _raw_dir_name_matches_checkpoint(candidate.name, checkpoint_run):
                matching_raw_dirs.append(candidate)
        if matching_raw_dirs:
            return matching_raw_dirs[-1]

    raw_run_dir = checkpoint_run.get("raw_run_dir")
    if raw_run_dir:
        resolved = _resolve_existing_path(raw_run_dir)
        if (resolved / "evidence.json").exists():
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


def _checkpoint_run_key(row: dict) -> tuple:
    return (
        row.get("review_key", ""),
        row.get("gatekeeper_preset", ""),
        row.get("orchestrator_policy", ""),
        row.get("orchestrator_preset", ""),
        int(row.get("run_index") or 1),
    )


def _raw_dir_token(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9]+", "", value).lower()


def _raw_dir_name_matches_checkpoint(raw_dir_name: str, checkpoint_run: dict) -> bool:
    review_key = str(checkpoint_run.get("review_key", ""))
    gatekeeper_preset = str(checkpoint_run.get("gatekeeper_preset", ""))
    orchestrator_preset = str(checkpoint_run.get("orchestrator_preset", ""))
    run_index = int(checkpoint_run.get("run_index") or 1)
    return (
        review_key in raw_dir_name
        and _raw_dir_token(gatekeeper_preset) in _raw_dir_token(raw_dir_name)
        and _raw_dir_token(orchestrator_preset) in _raw_dir_token(raw_dir_name)
        and f"run{run_index}" in raw_dir_name
    )


def _infer_checkpoint_run_from_raw_dir(
    raw_run_dir: Path,
    *,
    checkpoint: dict,
) -> dict | None:
    evidence_path = raw_run_dir / "evidence.json"
    if not evidence_path.exists():
        return None
    metrics_path = raw_run_dir / "metrics.json"
    if metrics_path.exists():
        with open(metrics_path, "r", encoding="utf-8") as f:
            metrics = json.load(f)
        return {
            "benchmark_run_id": metrics.get("benchmark_run_id", raw_run_dir.name),
            "review_key": metrics.get("review_key", ""),
            "gatekeeper_preset": metrics.get("gatekeeper_preset", ""),
            "orchestrator_policy": metrics.get("orchestrator_policy", ""),
            "orchestrator_preset": metrics.get("orchestrator_preset", ""),
            "run_index": int(metrics.get("run_index") or 1),
            "run_status": metrics.get("run_status", "completed"),
            "raw_run_dir": str(raw_run_dir),
        }

    review_key = next(
        (
            key
            for key in checkpoint.get("review_keys", [])
            if str(key) in raw_run_dir.name
        ),
        "",
    )
    model_presets = checkpoint.get("model_presets") or []
    gatekeeper_preset = next(
        (
            key
            for key in model_presets
            if _raw_dir_token(str(key)) in _raw_dir_token(raw_run_dir.name)
        ),
        model_presets[0] if len(model_presets) == 1 else "",
    )
    orchestrator_preset = checkpoint.get("orchestrator_preset", "")
    if orchestrator_preset == "match-gatekeeper":
        orchestrator_preset = gatekeeper_preset
    if not review_key or not gatekeeper_preset or not orchestrator_preset:
        return None
    run_match = re.search(r"run(\d+)", raw_run_dir.name)
    run_index = int(run_match.group(1)) if run_match else 1
    return {
        "benchmark_run_id": (
            f"{review_key}_{gatekeeper_preset}_{checkpoint.get('orchestrator_policy', '')}_"
            f"{orchestrator_preset}_run{run_index}"
        ),
        "review_key": review_key,
        "gatekeeper_preset": gatekeeper_preset,
        "orchestrator_policy": checkpoint.get("orchestrator_policy", ""),
        "orchestrator_preset": orchestrator_preset,
        "run_index": run_index,
        "run_status": "completed",
        "raw_run_dir": str(raw_run_dir),
    }


def _checkpoint_runs_with_recovered_raw_runs(
    experiment_dir: Path,
    *,
    checkpoint: dict,
) -> list[dict]:
    checkpoint_runs = list(checkpoint.get("completed_runs", []))
    seen_keys = {_checkpoint_run_key(row) for row in checkpoint_runs}
    review_keys = set(checkpoint.get("review_keys") or [])
    model_presets = set(checkpoint.get("model_presets") or [])
    orchestrator_policy = checkpoint.get("orchestrator_policy", "")
    orchestrator_preset = checkpoint.get("orchestrator_preset", "")
    raw_runs_root = experiment_dir / "_raw_runs"
    if not raw_runs_root.exists():
        return checkpoint_runs

    for raw_run_dir in sorted(path for path in raw_runs_root.iterdir() if path.is_dir()):
        recovered = _infer_checkpoint_run_from_raw_dir(raw_run_dir, checkpoint=checkpoint)
        if recovered is None:
            continue
        if review_keys and recovered.get("review_key") not in review_keys:
            continue
        if model_presets and recovered.get("gatekeeper_preset") not in model_presets:
            continue
        if recovered.get("orchestrator_policy") != orchestrator_policy:
            continue
        if recovered.get("orchestrator_preset") != orchestrator_preset:
            continue
        key = _checkpoint_run_key(recovered)
        if key not in seen_keys:
            checkpoint_runs.append(recovered)
            seen_keys.add(key)
    return checkpoint_runs


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
    for checkpoint_run in _checkpoint_runs_with_recovered_raw_runs(
        experiment_dir,
        checkpoint=checkpoint,
    ):
        run_source_dir = _raw_run_source_from_checkpoint(
            experiment_dir,
            checkpoint_run,
            selected_label_policies=selected_label_policies,
        )
        metrics_path = run_source_dir / "metrics.json"
        evidence_path = run_source_dir / "evidence.json"
        has_metrics = metrics_path.exists()
        if metrics_path.exists():
            with open(metrics_path, "r", encoding="utf-8") as f:
                metrics = json.load(f)
        else:
            metrics = {
                "review_key": checkpoint_run.get("review_key", ""),
                "gatekeeper_preset": checkpoint_run.get("gatekeeper_preset", ""),
                "orchestrator_policy": checkpoint_run.get("orchestrator_policy", ""),
                "orchestrator_preset": checkpoint_run.get("orchestrator_preset", ""),
                "run_index": checkpoint_run.get("run_index", 1),
                "run_status": "completed",
                "error": "",
            }

        review_key = checkpoint_run.get("review_key") or metrics["review_key"]
        review_case = review_case_by_key.get(review_key)
        if review_case is None:
            raise ValueError(
                f"Run '{checkpoint_run.get('benchmark_run_id', run_source_dir.name)}' "
                f"references review '{review_key}', which was not found in suite '{suite_name}'."
            )

        review = _load_review_cached(review_case.key, review_case.split)
        if review is None:
            raise ValueError(
                f"Unable to load review '{review_case.key}' from split "
                f"'{review_case.split}' while backfilling '{experiment_dir.name}'."
            )

        screening_decisions = _read_screening_decisions(evidence_path)
        run_status = metrics.get("run_status", "completed")
        if not has_metrics and run_status != "error":
            status_metrics = compute_screening_metrics(
                review,
                screening_decisions,
                label_policy=selected_label_policies[0],
            )
            run_status = "completed" if status_metrics.get("parse_success") else "incomplete"

        raw_runs.append({
            "suite_name": suite_name,
            "review_case": review_case,
            "review": review,
            "screening_decisions": screening_decisions,
            "gatekeeper_model": resolve_model(metrics["gatekeeper_preset"], strict=False),
            "orchestrator_model": resolve_model(metrics["orchestrator_preset"], strict=False),
            "orchestrator_policy": metrics["orchestrator_policy"],
            "run_index": int(metrics["run_index"]),
            "duration_seconds": float(metrics.get("duration_seconds", 0.0)),
            "raw_run_dir": run_source_dir,
            "run_status": run_status,
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
        trace_snapshots = _snapshot_policy_trace_files(policy_dir)
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
        _restore_missing_policy_trace_files(policy_dir, trace_snapshots)
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
            for key in ("loop_mode", "chunk_count", "chunk_size", "orchestrator_max_steps")
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

        review = _load_review_cached(review_case.key, review_case.split)
        if review is None:
            raise ValueError(
                f"Unable to load review '{review_case.key}' from split "
                f"'{review_case.split}' while backfilling '{experiment_dir.name}'."
            )

        raw_runs.append({
            "suite_name": suite_name,
            "review_case": review_case,
            "review": review,
            "screening_decisions": _read_screening_decisions(evidence_path),
            "gatekeeper_model": resolve_model(metrics["gatekeeper_preset"], strict=False),
            "orchestrator_model": resolve_model(metrics["orchestrator_preset"], strict=False),
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
        trace_snapshots = _snapshot_policy_trace_files(policy_dir)
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
        _restore_missing_policy_trace_files(policy_dir, trace_snapshots)
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
