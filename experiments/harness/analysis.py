"""
Post-run analysis for Mentor suite experiment directories.

Reads ``_raw_runs/*/evidence.json`` + ``run.json``, scores against gold labels,
materializes per-policy views, and writes summary/leaderboard artifacts.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

from experiments.harness.common import sort_raw_runs as _sort_raw_runs
from experiments.harness.comparison_reports import write_policy_comparison_report
from experiments.harness.html_reports import write_policy_html_report
from experiments.harness.metrics import SCREENING_LABEL_POLICIES
from experiments.catalog import resolve_model
from experiments.harness.notebooks import write_policy_eda_notebook
from experiments.suites.review_suites import ScreeningBenchmarkReview, get_review_suite
from experiments.harness.runner import (
    _checkpoint_policy_outputs,
    _policy_output_record,
    _write_benchmark_checkpoint,
)
from experiments.harness.totals import register_canonical_sources_from_experiment
from experiments.dataset import load_review
from experiments.evidence import read_existing_decisions

logger = logging.getLogger("experiments.analysis")


def _read_json(path: Path) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _review_case_from_run(run_meta: dict, suite_name: str) -> ScreeningBenchmarkReview:
    review_key = run_meta["review_key"]
    for review in get_review_suite(suite_name):
        if review.key == review_key:
            return review
    # Fallback when suite no longer lists the review.
    return ScreeningBenchmarkReview(
        key=run_meta.get("review_url") or review_key,
        split=run_meta.get("split", "dev"),
    )


def load_raw_runs_from_experiment(experiment_dir: Path) -> tuple[list[dict], dict]:
    """
    Load raw runs from a mentor suite directory (or legacy checkpoint).

    Returns ``(raw_runs, metadata)`` where each raw_run matches the shape
    expected by ``_materialize_policy_outputs``.
    """
    experiment_dir = Path(experiment_dir)
    manifest_path = experiment_dir / "suite_manifest.json"
    checkpoint_path = experiment_dir / "benchmark_checkpoint.json"

    metadata: dict = {}
    if manifest_path.exists():
        metadata = _read_json(manifest_path)
    elif checkpoint_path.exists():
        metadata = _read_json(checkpoint_path)

    suite_name = metadata.get("suite") or experiment_dir.name
    raw_root = experiment_dir / "_raw_runs"
    if not raw_root.exists():
        # Legacy layout sometimes used raw_runs/
        alt = experiment_dir / "raw_runs"
        raw_root = alt if alt.exists() else raw_root

    raw_runs: list[dict] = []
    if not raw_root.exists():
        return [], metadata

    for run_dir in sorted(p for p in raw_root.iterdir() if p.is_dir()):
        run_json_path = run_dir / "run.json"
        metrics_path = run_dir / "metrics.json"
        if run_json_path.exists():
            run_meta = _read_json(run_json_path)
        elif metrics_path.exists():
            run_meta = _read_json(metrics_path)
        else:
            logger.warning("Skipping %s: no run.json or metrics.json", run_dir.name)
            continue

        suite = run_meta.get("suite") or suite_name
        review_case = _review_case_from_run(run_meta, suite)
        review = load_review(review_case.key, review_case.split)
        if review is None:
            logger.warning(
                "Skipping %s: unable to load review %s",
                run_dir.name,
                review_case.key,
            )
            continue

        gk_key = run_meta.get("gatekeeper_preset") or "env_default"
        orch_key = run_meta.get("orchestrator_preset") or gk_key
        gatekeeper_model = resolve_model(gk_key, strict=False)
        orchestrator_model = resolve_model(orch_key, strict=False)

        decisions = read_existing_decisions(run_dir)
        status = run_meta.get("status") or run_meta.get("run_status") or "completed"
        telemetry = dict(run_meta.get("telemetry") or {})
        if run_meta.get("provider_usage"):
            telemetry = {**telemetry, "provider_usage": run_meta["provider_usage"]}

        raw_runs.append({
            "review_case": review_case,
            "review": review,
            "screening_decisions": decisions,
            "gatekeeper_model": gatekeeper_model,
            "orchestrator_model": orchestrator_model,
            "orchestrator_policy": run_meta.get("orchestrator_policy")
            or run_meta.get("config_label")
            or "default",
            "suite_name": suite,
            "run_index": int(run_meta.get("run_index") or 1),
            "duration_seconds": float(run_meta.get("duration_seconds") or 0.0),
            "raw_run_dir": run_dir,
            "run_status": status,
            "screening_attempt_count": int(run_meta.get("screening_attempt_count") or 1),
            "rerun_triggered": bool(run_meta.get("rerun_triggered") or False),
            "benchmark_architecture": run_meta.get("benchmark_architecture")
            or metadata.get("benchmark_architecture")
            or "batch",
            "telemetry": telemetry,
            "error": run_meta.get("error") or "",
            "error_type": run_meta.get("error_type") or "",
        })

    raw_runs = _sort_raw_runs(raw_runs)
    if not metadata.get("suite"):
        metadata["suite"] = suite_name
    if not metadata.get("model_presets"):
        metadata["model_presets"] = list(
            dict.fromkeys(r["gatekeeper_model"].key for r in raw_runs)
        )
    if not metadata.get("review_keys"):
        metadata["review_keys"] = list(
            dict.fromkeys(r["review_case"].key for r in raw_runs)
        )
    if not metadata.get("repeats"):
        metadata["repeats"] = max((r["run_index"] for r in raw_runs), default=1)
    if not metadata.get("orchestrator_policy"):
        metadata["orchestrator_policy"] = "default"
    if not metadata.get("orchestrator_preset"):
        metadata["orchestrator_preset"] = (
            raw_runs[0]["orchestrator_model"].key if raw_runs else ""
        )
    return raw_runs, metadata


def analyze_experiment(
    experiment_dir: Path | str,
    *,
    label_policies: list[str] | None = None,
    execute_policy_notebooks: bool = False,
    register_totals: bool = True,
) -> dict:
    """
    Score raw runs and materialize policy summaries for an experiment directory.
    """
    experiment_dir = Path(experiment_dir)
    if not experiment_dir.exists():
        raise FileNotFoundError(f"Experiment directory not found: {experiment_dir}")

    raw_runs, metadata = load_raw_runs_from_experiment(experiment_dir)
    if not raw_runs:
        raise ValueError(f"No raw runs found under {experiment_dir / '_raw_runs'}")

    selected = label_policies or list(SCREENING_LABEL_POLICIES)
    suite_name = metadata["suite"]
    repeats = int(metadata.get("repeats") or 1)
    review_keys = list(metadata.get("review_keys") or [])
    model_presets = list(metadata.get("model_presets") or [])
    orchestrator_policy = metadata.get("orchestrator_policy") or "default"
    orchestrator_preset = metadata.get("orchestrator_preset") or ""
    architecture = metadata.get("benchmark_architecture") or "batch"

    policy_summaries = _checkpoint_policy_outputs(
        experiment_dir,
        suite_name=suite_name,
        repeats=repeats,
        review_keys=review_keys,
        model_presets=model_presets,
        orchestrator_policy=orchestrator_policy,
        orchestrator_preset=orchestrator_preset,
        selected_label_policies=selected,
        raw_runs=raw_runs,
    )

    # Enrich with notebooks / HTML when requested.
    for label_policy, record in list(policy_summaries.items()):
        policy_dir = Path(record["directory"])
        try:
            html_info = write_policy_html_report(policy_dir)
        except Exception as exc:
            logger.warning("HTML report failed for %s: %s", label_policy, exc)
            html_info = {}
        notebook_info = {}
        if execute_policy_notebooks:
            try:
                notebook_info = write_policy_eda_notebook(
                    policy_dir, execute=True
                )
            except Exception as exc:
                logger.warning("Notebook failed for %s: %s", label_policy, exc)
                notebook_info = {"execution_error": str(exc)}
        policy_summaries[label_policy] = _policy_output_record(
            policy_dir,
            record.get("summary") or {},
            notebook_info=notebook_info,
            html_report_info=html_info if isinstance(html_info, dict) else {},
        )

    comparison_path = None
    try:
        comparison = write_policy_comparison_report(experiment_dir)
        if isinstance(comparison, dict):
            comparison_path = comparison.get("report_path")
        else:
            comparison_path = str(comparison) if comparison else None
    except Exception as exc:
        logger.warning("Comparison report failed: %s", exc)

    _write_benchmark_checkpoint(
        experiment_dir,
        suite_name=suite_name,
        benchmark_architecture=architecture,
        repeats=repeats,
        review_keys=review_keys,
        model_presets=model_presets,
        orchestrator_policy=orchestrator_policy,
        orchestrator_preset=orchestrator_preset,
        selected_label_policies=selected,
        total_expected_raw_runs=len(raw_runs),
        raw_runs=raw_runs,
        policy_summaries=policy_summaries,
        comparison_report=comparison_path,
        extra_metadata={"source": "experiments.analyze"},
    )

    if register_totals:
        try:
            register_canonical_sources_from_experiment(experiment_dir)
        except Exception as exc:
            logger.warning("Totals registration failed: %s", exc)

    summary = {
        "experiment_dir": str(experiment_dir),
        "raw_run_count": len(raw_runs),
        "label_policies": selected,
        "policy_summaries": {
            key: {
                "directory": value.get("directory"),
                "summary_csv": value.get("summary_csv"),
                "leaderboard_markdown": value.get("leaderboard_markdown"),
            }
            for key, value in policy_summaries.items()
        },
    }
    logger.info(
        "Analyzed %s raw runs in %s",
        len(raw_runs),
        experiment_dir,
    )
    return summary
