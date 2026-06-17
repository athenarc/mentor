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
from bastirr.benchmarking.runner import _materialize_policy_outputs
from bastirr.data import load_review


_POLICY_DIR_NAMES = {
    "include_label_0_5": "include_policy",
    "exclude_label_0_5": "exclude_policy",
}


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


def backfill_policy_views(
    experiment_dir: Path,
    *,
    label_policies: list[str] | None = None,
    remove_flat_outputs: bool = True,
    remove_shared_runs: bool = True,
    execute_policy_notebooks: bool = True,
) -> dict:
    """
    Backfill an older flat screening benchmark directory into policy subfolders.

    Reuses the existing shared raw run artifacts under ``runs/`` and derives
    separate ``include_policy/`` and ``exclude_policy/`` views without rerunning
    the models.
    """
    experiment_dir = Path(experiment_dir)
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

        review = load_review(review_case.review_url, review_case.split)
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
    }
