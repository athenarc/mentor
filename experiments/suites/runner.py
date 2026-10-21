"""
Suite runner: reviews × profiles × repeats.

Loads Cochrane reviews from the dataset, writes Mentor ``review.json``,
and invokes ``uv run mentor`` as an external process per cell.

Writes raw run directories under ``_raw_runs/``. Metrics via ``experiments analyze``.
"""

from __future__ import annotations

import json
import logging
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any

from experiments.catalog import resolve_model
from experiments.dataset import load_review
from experiments.evidence import read_existing_decisions
from experiments.paths import OUTPUT_DIR, PROJECT_ROOT
from experiments.review_json import normalize_mode, write_review_json
from experiments.suites.review_suites import (
    ScreeningBenchmarkReview,
    SuiteRunConfig,
    expand_suite_run_config,
    resolve_review_selection,
)

logger = logging.getLogger("experiments.suites")


def architecture_name(batch_size: int | None) -> str:
    if batch_size is None:
        return "batch"
    if batch_size == 1:
        return "single_study"
    return f"chunked_{batch_size}"


def _run_name(
    review_case: ScreeningBenchmarkReview,
    *,
    gatekeeper_key: str,
    orchestrator_key: str,
    run_index: int,
) -> str:
    safe_gk = gatekeeper_key.replace("/", "_")
    safe_orch = orchestrator_key.replace("/", "_")
    return f"{review_case.path_slug}__gk-{safe_gk}__orch-{safe_orch}__r{run_index}"


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)


def _patch_run_json(run_dir: Path, **updates: Any) -> dict[str, Any]:
    path = run_dir / "run.json"
    payload: dict[str, Any] = {}
    if path.exists():
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            payload = {}
    payload.update(updates)
    _write_json(path, payload)
    return payload


def _mentor_cmd(
    *,
    review_json_path: Path,
    profile_key: str,
    batch_size: int | None,
    output_root: Path,
    run_name: str,
    hide_subagent_steps: bool,
) -> list[str]:
    cmd = [
        sys.executable,
        "-m",
        "mentor.cli",
        "--review",
        str(review_json_path),
        "--profile",
        profile_key,
        "--output-root",
        str(output_root),
        "--run-name",
        run_name,
    ]
    if batch_size is not None:
        cmd.extend(["--batch-size", str(batch_size)])
    if hide_subagent_steps:
        cmd.append("--hide-subagent-steps")
    return cmd


def run_single_review(
    *,
    suite_name: str,
    review_case: ScreeningBenchmarkReview,
    agents: dict[str, str],
    profile_key: str,
    config_label: str,
    run_index: int,
    output_root: Path,
    stages: str = "screening-only",
    batch_size: int | None = None,
    include_subagent_steps: bool = True,
) -> dict[str, Any]:
    """Execute one review × profile × repeat via external ``mentor`` CLI."""
    gatekeeper_key = (
        agents.get("gatekeeper") or agents.get("shared") or next(iter(agents.values()))
    )
    orchestrator_key = (
        agents.get("orchestrator") or agents.get("shared") or gatekeeper_key
    )
    gatekeeper_model = resolve_model(gatekeeper_key, strict=False)
    orchestrator_model = resolve_model(orchestrator_key, strict=False)

    dataset_review = load_review(review_case.key, review_case.split)
    if dataset_review is None:
        raise ValueError(
            f"Unable to load review '{review_case.key}' from split '{review_case.split}'."
        )

    mode = normalize_mode(stages)
    run_name = _run_name(
        review_case,
        gatekeeper_key=gatekeeper_key,
        orchestrator_key=orchestrator_key,
        run_index=run_index,
    )
    run_dir = output_root / run_name
    run_dir.mkdir(parents=True, exist_ok=True)

    review_json_path = run_dir / "review.json"
    write_review_json(
        review_json_path,
        mode=mode,
        title=dataset_review.title,
        objective=dataset_review.objective,
        background=dataset_review.background,
        selection_criteria=dataset_review.selection_criteria,
        studies=dataset_review.studies if mode == "screening-only" else None,
    )

    suite_meta = {
        "suite": suite_name,
        "review_key": review_case.key,
        "review_url": dataset_review.review_url,
        "split": review_case.split,
        "run_index": run_index,
        "stages": mode,
        "mode": mode,
        "screening_batch_size": batch_size,
        "benchmark_architecture": architecture_name(batch_size),
        "profile": profile_key,
        "agents": agents,
        "config_label": config_label,
        "gatekeeper_preset": gatekeeper_model.key,
        "gatekeeper_model_label": gatekeeper_model.model_label,
        "orchestrator_preset": orchestrator_model.key,
        "orchestrator_model_label": orchestrator_model.model_label,
        "error_type": "",
    }

    cmd = _mentor_cmd(
        review_json_path=review_json_path,
        profile_key=profile_key,
        batch_size=batch_size,
        output_root=output_root,
        run_name=run_name,
        hide_subagent_steps=not include_subagent_steps,
    )
    logger.info("Invoking Mentor: %s", " ".join(cmd))
    started_at = time.perf_counter()
    run_status = "completed"
    error = ""
    error_type = ""

    try:
        completed = subprocess.run(
            cmd,
            cwd=str(PROJECT_ROOT),
            env=os.environ.copy(),
            check=False,
        )
        if completed.returncode != 0:
            run_status = "error"
            error_type = "MentorExitError"
            error = f"mentor exited with code {completed.returncode}"
    except OSError as exc:
        run_status = "error"
        error_type = type(exc).__name__
        error = f"{error_type}: {exc}"
        logger.exception("Failed to launch mentor for %s", run_name)

    duration = time.perf_counter() - started_at
    # Prefer Mentor's own run.json status when present.
    existing: dict[str, Any] = {}
    run_json_path = run_dir / "run.json"
    if run_json_path.exists():
        try:
            existing = json.loads(run_json_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            existing = {}
        if existing.get("status"):
            run_status = str(existing["status"])
        if existing.get("error"):
            error = str(existing["error"])
        if "ContextOverflow" in error or "context_overflow" in error.lower():
            run_status = "incomplete"
            error_type = "context_overflow"

    decisions = read_existing_decisions(run_dir)
    if run_status == "completed" and mode == "screening-only":
        if len(decisions) != len(dataset_review.studies):
            run_status = "incomplete"
            error = error or (
                f"Expected {len(dataset_review.studies)} decisions, "
                f"found {len(decisions)}."
            )

    return _patch_run_json(
        run_dir,
        **suite_meta,
        status=run_status,
        error=error,
        error_type=error_type,
        duration_seconds=existing.get("duration_seconds", duration),
        n_studies=len(dataset_review.studies),
        decision_count=len(decisions),
        run_dir=str(run_dir),
        provider_usage=existing.get("provider_usage") or {},
    )


def run_suite(
    *,
    suite_name: str,
    review_keys: list[str] | None = None,
    profiles: list[str] | None = None,
    repeats: int | None = None,
    batch_size: int | None = None,
    stages: str | None = None,
    include_subagent_steps: bool = True,
    resume_dir: Path | None = None,
    output_root: Path | None = None,
    batch_size_set: bool = False,
) -> Path:
    """Run a suite grid via external Mentor processes; return experiment dir."""
    run_config: SuiteRunConfig = expand_suite_run_config(
        suite_name,
        profiles_override=profiles,
        repeats_override=repeats,
        batch_size_override=batch_size if batch_size_set else ...,
        stages_override=stages,
    )
    reviews = resolve_review_selection(suite_name, review_keys)

    if resume_dir is not None:
        experiment_dir = Path(resume_dir)
        raw_root = experiment_dir / "_raw_runs"
        raw_root.mkdir(parents=True, exist_ok=True)
    else:
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        arch = architecture_name(run_config.batch_size)
        base = (
            Path(output_root)
            if output_root
            else Path(OUTPUT_DIR) / "screening_benchmarks"
        )
        experiment_dir = base / f"{suite_name}_{arch}_{stamp}"
        raw_root = experiment_dir / "_raw_runs"
        raw_root.mkdir(parents=True, exist_ok=True)

    manifest = {
        "suite": suite_name,
        "stages": run_config.stages,
        "batch_size": run_config.batch_size,
        "repeats": run_config.repeats,
        "benchmark_architecture": architecture_name(run_config.batch_size),
        "configurations": [
            {
                "profile": c.profile_key,
                "label": c.label,
                "agents": c.agents,
            }
            for c in run_config.configurations
        ],
        "reviews": [r.key for r in reviews],
        "created_at": datetime.now().isoformat(timespec="seconds"),
    }
    _write_json(experiment_dir / "suite_manifest.json", manifest)

    completed: set[str] = set()
    if resume_dir is not None and raw_root.exists():
        for path in raw_root.iterdir():
            run_json = path / "run.json"
            if not run_json.exists():
                continue
            try:
                payload = json.loads(run_json.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                continue
            if payload.get("status") == "completed":
                completed.add(path.name)

    results: list[dict] = []
    for review_case in reviews:
        for config in run_config.configurations:
            for run_index in range(1, run_config.repeats + 1):
                gatekeeper_key = (
                    config.agents.get("gatekeeper")
                    or config.agents.get("shared")
                    or next(iter(config.agents.values()))
                )
                orchestrator_key = (
                    config.agents.get("orchestrator")
                    or config.agents.get("shared")
                    or gatekeeper_key
                )
                name = _run_name(
                    review_case,
                    gatekeeper_key=gatekeeper_key,
                    orchestrator_key=orchestrator_key,
                    run_index=run_index,
                )
                if name in completed:
                    logger.info("Skipping completed run %s", name)
                    continue
                logger.info(
                    "Running %s (stages=%s batch_size=%s)",
                    name,
                    run_config.stages,
                    run_config.batch_size,
                )
                result = run_single_review(
                    suite_name=suite_name,
                    review_case=review_case,
                    agents=config.agents,
                    profile_key=config.profile_key,
                    config_label=config.label,
                    run_index=run_index,
                    output_root=raw_root,
                    stages=run_config.stages,
                    batch_size=run_config.batch_size,
                    include_subagent_steps=include_subagent_steps,
                )
                results.append(result)

    _write_json(
        experiment_dir / "suite_results.json",
        {"runs": results, "completed_count": len(results)},
    )
    logger.info("Suite complete: %s (%s new runs)", experiment_dir, len(results))
    return experiment_dir
