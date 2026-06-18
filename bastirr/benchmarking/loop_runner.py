"""
Core runner for the looped Gatekeeper screening benchmark harness.
"""

from __future__ import annotations

import json
import logging
import time
from datetime import datetime
from pathlib import Path

from bastirr.agents.screening_loop_orchestrator import (
    create_screening_chunk_loop_orchestrator_agent,
    create_screening_loop_orchestrator_agent,
)
from bastirr.benchmarking.comparison_reports import write_policy_comparison_report
from bastirr.benchmarking.html_reports import write_policy_html_report
from bastirr.benchmarking.metrics import SCREENING_LABEL_POLICIES, compute_screening_metrics
from bastirr.benchmarking.model_presets import (
    ResolvedModelPreset,
    get_model_preset,
    resolve_model_presets,
)
from bastirr.benchmarking.notebooks import write_policy_eda_notebook
from bastirr.benchmarking.review_suites import (
    ScreeningBenchmarkReview,
    resolve_review_selection,
)
from bastirr.benchmarking.runner import (
    _checkpoint_policy_outputs,
    _policy_output_record,
    _raw_runs_checkpoint_root,
    _read_screening_decisions,
    _run_name,
    _validate_review_case,
    _write_benchmark_checkpoint,
)
from bastirr.benchmarking.telemetry import collect_activity_telemetry
from bastirr.benchmarking.totals import register_canonical_sources_from_experiment
from bastirr.config import OUTPUT_DIR
from bastirr.data import load_review
from bastirr.logging_utils import make_step_callbacks, setup_run_logging
from bastirr.run_demo import review_to_json
from bastirr.tools.screening_benchmark_tools import _write_screening_artifacts
from bastirr.tools.search_tools import load_review_data

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
)
logger = logging.getLogger("bastirr.screening_loop_benchmark")


LOOP_BENCHMARK_ARCHITECTURE = "loop_orchestrator_v1"
LOOP_CHUNK_BENCHMARK_ARCHITECTURE = "loop_chunk_orchestrator_v1"
_MAX_LOOP_ATTEMPTS = 2


def _experiment_model_suffix(model_keys: list[str]) -> str:
    """Return a bounded, readable model suffix for loop experiment folders."""
    if len(model_keys) == 1:
        return model_keys[0]
    return f"models{len(model_keys)}"


def _loop_experiment_root(suite_name: str, model_keys: list[str]) -> Path:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    model_suffix = _experiment_model_suffix(model_keys)
    path = OUTPUT_DIR / "screening_benchmarks" / f"{timestamp}_{suite_name}_loop_{model_suffix}"
    path.mkdir(parents=True, exist_ok=True)
    return path


def _loop_architecture_name(loop_mode: str) -> str:
    if loop_mode == "chunked":
        return LOOP_CHUNK_BENCHMARK_ARCHITECTURE
    return LOOP_BENCHMARK_ARCHITECTURE


def _loop_experiment_root_for_mode(suite_name: str, model_keys: list[str], loop_mode: str) -> Path:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    model_suffix = _experiment_model_suffix(model_keys)
    mode_suffix = "loop_chunked" if loop_mode == "chunked" else "loop"
    path = OUTPUT_DIR / "screening_benchmarks" / f"{timestamp}_{suite_name}_{mode_suffix}_{model_suffix}"
    path.mkdir(parents=True, exist_ok=True)
    return path


def _read_json(path: Path) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _policy_dir_for_label(experiment_dir: Path, label_policy: str) -> Path:
    if label_policy == "include_label_0_5":
        return experiment_dir / "include_policy"
    if label_policy == "exclude_label_0_5":
        return experiment_dir / "exclude_policy"
    return experiment_dir / label_policy


def _missing_study_indices(review, screening_decisions: list[dict]) -> list[int]:
    completed: set[int] = set()
    for decision in screening_decisions:
        try:
            index = int(decision.get("study_index", 0))
        except (TypeError, ValueError):
            continue
        if 1 <= index <= len(review.studies):
            completed.add(index)
    return [
        index
        for index in range(1, len(review.studies) + 1)
        if index not in completed
    ]


def _default_chunk_count(n_studies: int) -> int:
    if n_studies <= 25:
        return 1
    if n_studies <= 50:
        return 2
    if n_studies <= 100:
        return 4
    if n_studies <= 150:
        return 5
    if n_studies <= 225:
        return 6
    return max(6, (n_studies + 39) // 40)


def _chunk_indices(indices: list[int], *, chunk_count: int | None = None, chunk_size: int | None = None) -> list[list[int]]:
    if not indices:
        return []
    if chunk_size is not None:
        if chunk_size < 1:
            raise ValueError("--chunk-size must be at least 1")
        return [
            indices[offset:offset + chunk_size]
            for offset in range(0, len(indices), chunk_size)
        ]

    resolved_chunk_count = chunk_count or _default_chunk_count(len(indices))
    if resolved_chunk_count < 1:
        raise ValueError("--chunk-count must be at least 1")
    resolved_chunk_count = min(resolved_chunk_count, len(indices))
    base_size, remainder = divmod(len(indices), resolved_chunk_count)
    chunks: list[list[int]] = []
    cursor = 0
    for chunk_index in range(resolved_chunk_count):
        size = base_size + (1 if chunk_index < remainder else 0)
        chunks.append(indices[cursor:cursor + size])
        cursor += size
    return chunks


def _build_loop_screening_task(
    review,
    output_dir: Path,
    *,
    study_indices: list[int],
    expected_n_studies: int,
    retry_note: str | None = None,
) -> str:
    retry_block = ""
    if retry_note:
        retry_block = f"Retry/resume guidance:\n{retry_note}\n\n"
    return (
        "Conduct only title/abstract screening for the listed study indices.\n\n"
        f"Review title: {review.title}\n\n"
        f"Review background:\n{review.background}\n\n"
        f"Review objective:\n{review.objective}\n\n"
        f"Selection criteria:\n{review.selection_criteria}\n\n"
        f"Output directory: {output_dir}\n"
        f"Expected study decisions for full review: {expected_n_studies}\n"
        f"Study indices to process as a JSON array: {json.dumps(study_indices)}\n\n"
        f"{retry_block}"
        "Execute the looped screening workflow:\n"
        "1. Parse the study index JSON array from this task.\n"
        "2. For each listed index, call get_candidate_study_json(index).\n"
        "3. Call the gatekeeper managed agent with that one-study JSON payload only.\n"
        "4. Immediately call append_screening_decision_json with the raw Gatekeeper "
        "response, output_dir, expected_study_index=index, and expected_n_studies.\n"
        "5. Keep observations short; do not print study JSON or Gatekeeper responses.\n"
        "6. Return format_screening_progress_summary(review_title, output_dir) as final_answer.\n"
        "Do not classify studies in Orchestrator code and do not fabricate fallback decisions.\n"
    )


def _build_chunk_loop_screening_task(
    review,
    output_dir: Path,
    *,
    chunk_indices: list[int],
    expected_n_studies: int,
    chunk_number: int,
    chunk_total: int,
    retry_note: str | None = None,
) -> str:
    retry_block = ""
    if retry_note:
        retry_block = f"Retry guidance:\n{retry_note}\n\n"
    return (
        "Conduct only title/abstract screening for the listed bounded study chunk.\n\n"
        f"Review title: {review.title}\n\n"
        f"Review background:\n{review.background}\n\n"
        f"Review objective:\n{review.objective}\n\n"
        f"Selection criteria:\n{review.selection_criteria}\n\n"
        f"Output directory: {output_dir}\n"
        f"Expected study decisions for full review: {expected_n_studies}\n"
        f"Chunk number: {chunk_number} of {chunk_total}\n"
        f"Chunk study indices as JSON array: {json.dumps(chunk_indices)}\n\n"
        f"{retry_block}"
        "Execute the mini-batch loop screening workflow:\n"
        "1. Parse the chunk study index JSON array from this task.\n"
        "2. Call get_candidate_studies_chunk_json with that JSON array string.\n"
        "3. Call the gatekeeper managed agent with that one chunk payload only.\n"
        "4. Immediately call append_screening_chunk_decisions_json with the raw "
        "Gatekeeper response, output_dir, expected_study_indices_json, and expected_n_studies.\n"
        "5. Keep observations short; do not print study JSON or Gatekeeper responses.\n"
        "6. Return format_screening_progress_summary(review_title, output_dir) as final_answer.\n"
        "Do not classify studies in Orchestrator code and do not fabricate fallback decisions.\n"
    )


def run_screening_loop_review(
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
) -> dict:
    """
    Execute one looped screening benchmark run for a single review/model pair.
    """
    review = load_review(review_case.review_url, review_case.split)
    if review is None:
        raise ValueError(
            f"Unable to load review '{review_case.review_url}' from split '{review_case.split}'."
        )
    _validate_review_case(review_case, review, label_policy=label_policy)
    load_review_data(review_to_json(review))

    run_dir, agent_logger, activity_logger = setup_run_logging(
        review.title,
        include_subagent_steps=include_subagent_steps,
        output_root=output_root,
        run_name=_run_name(
            review_case,
            gatekeeper_model,
            orchestrator_policy,
            orchestrator_model,
            run_index,
        ),
    )
    step_callbacks = make_step_callbacks(activity_logger)

    activity_logger.log_metadata("Benchmark suite", suite_name)
    activity_logger.log_metadata("Benchmark architecture", LOOP_BENCHMARK_ARCHITECTURE)
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
    evidence_path = run_dir / "evidence.json"
    screening_attempt_count = 0
    resume_count = 0
    rerun_triggered = False
    last_attempt_error = ""
    telemetry: dict = {}

    activity_logger.mark_pipeline_start()
    started_at = time.perf_counter()
    try:
        _write_screening_artifacts(
            run_dir,
            _read_screening_decisions(evidence_path),
            expected_n_studies=len(review.studies),
        )
        retry_note = None
        for attempt_index in range(1, _MAX_LOOP_ATTEMPTS + 1):
            decisions = _read_screening_decisions(evidence_path)
            missing_indices = _missing_study_indices(review, decisions)
            if not missing_indices:
                break

            screening_attempt_count = attempt_index
            if attempt_index > 1:
                rerun_triggered = True
                resume_count += 1
                retry_message = (
                    f"Resuming looped screening attempt {attempt_index}/"
                    f"{_MAX_LOOP_ATTEMPTS}; {len(missing_indices)} studies remain."
                )
                logger.warning(
                    "%s review=%s gatekeeper=%s",
                    retry_message,
                    review_case.key,
                    gatekeeper_model.key,
                )
                agent_logger.log(retry_message)

            try:
                loop_orchestrator = create_screening_loop_orchestrator_agent(
                    orchestrator_model.create_model(),
                    gatekeeper_model.create_model(),
                    step_callbacks=step_callbacks,
                    logger=agent_logger,
                )
                loop_orchestrator.run(
                    _build_loop_screening_task(
                        review,
                        run_dir,
                        study_indices=missing_indices,
                        expected_n_studies=len(review.studies),
                        retry_note=retry_note,
                    )
                )
            except Exception as attempt_exc:
                last_attempt_error = f"{type(attempt_exc).__name__}: {attempt_exc}"
                retry_note = (
                    "The previous loop attempt failed before all missing studies "
                    "were saved. Continue from the remaining unsaved study indices. "
                    f"Error: {last_attempt_error}"
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
            retry_note = (
                f"The previous loop attempt saved {attempt_metrics['screening_decision_count']}/"
                f"{attempt_metrics['n_studies']} unique decisions. Continue only "
                "with the missing study indices and append one decision per study."
            )

        decisions = _read_screening_decisions(evidence_path)
        final_metrics = compute_screening_metrics(
            review,
            decisions,
            label_policy=label_policy,
        )
        if final_metrics["parse_success"]:
            run_status = "completed"
        elif last_attempt_error and final_metrics["screening_decision_count"] == 0:
            run_status = "error"
            error = last_attempt_error
        else:
            run_status = "incomplete"
            error = last_attempt_error
    finally:
        duration_seconds = time.perf_counter() - started_at
        activity_path = activity_logger.finalize(model=None)
        telemetry = collect_activity_telemetry(
            activity_logger,
            duration_seconds=duration_seconds,
            n_studies=len(review.studies),
            retry_count=max(screening_attempt_count - 1, 0),
            resume_count=resume_count,
        )
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
        "screening_attempt_count": screening_attempt_count,
        "rerun_triggered": rerun_triggered,
        "benchmark_architecture": LOOP_BENCHMARK_ARCHITECTURE,
        "telemetry": telemetry,
    }


def run_screening_chunk_loop_review(
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
    chunk_count: int | None = None,
    chunk_size: int | None = None,
) -> dict:
    """
    Execute one chunked loop screening benchmark run for a single review/model pair.
    """
    review = load_review(review_case.review_url, review_case.split)
    if review is None:
        raise ValueError(
            f"Unable to load review '{review_case.review_url}' from split '{review_case.split}'."
        )
    _validate_review_case(review_case, review, label_policy=label_policy)
    load_review_data(review_to_json(review))

    benchmark_architecture = LOOP_CHUNK_BENCHMARK_ARCHITECTURE
    run_dir, agent_logger, activity_logger = setup_run_logging(
        review.title,
        include_subagent_steps=include_subagent_steps,
        output_root=output_root,
        run_name=_run_name(
            review_case,
            gatekeeper_model,
            orchestrator_policy,
            orchestrator_model,
            run_index,
        ),
    )
    step_callbacks = make_step_callbacks(activity_logger)

    planned_chunks = _chunk_indices(
        list(range(1, len(review.studies) + 1)),
        chunk_count=chunk_count,
        chunk_size=chunk_size,
    )

    activity_logger.log_metadata("Benchmark suite", suite_name)
    activity_logger.log_metadata("Benchmark architecture", benchmark_architecture)
    activity_logger.log_metadata("Loop mode", "chunked")
    activity_logger.log_metadata("Review key", review_case.key)
    activity_logger.log_metadata("Review URL", review.review_url)
    activity_logger.log_metadata("Dataset split", review_case.split)
    activity_logger.log_metadata("Studies", str(len(review.studies)))
    activity_logger.log_metadata("Chunk count", str(len(planned_chunks)))
    activity_logger.log_metadata(
        "Chunk sizes",
        ", ".join(str(len(chunk)) for chunk in planned_chunks),
    )
    activity_logger.log_metadata("Gatekeeper preset", gatekeeper_model.key)
    activity_logger.log_metadata("Gatekeeper model", gatekeeper_model.model_label)
    activity_logger.log_metadata("Orchestrator preset", orchestrator_model.key)
    activity_logger.log_metadata("Orchestrator model", orchestrator_model.model_label)
    activity_logger.log_metadata("Orchestrator policy", orchestrator_policy)
    activity_logger.log_metadata("Gold label policy", label_policy)

    run_status = "completed"
    error = ""
    evidence_path = run_dir / "evidence.json"
    screening_attempt_count = 0
    resume_count = 0
    rerun_triggered = False
    last_attempt_error = ""
    telemetry: dict = {}

    activity_logger.mark_pipeline_start()
    started_at = time.perf_counter()
    try:
        _write_screening_artifacts(
            run_dir,
            _read_screening_decisions(evidence_path),
            expected_n_studies=len(review.studies),
        )

        for attempt_index in range(1, _MAX_LOOP_ATTEMPTS + 1):
            decisions = _read_screening_decisions(evidence_path)
            missing_indices = _missing_study_indices(review, decisions)
            if not missing_indices:
                break

            screening_attempt_count = attempt_index
            if attempt_index > 1:
                rerun_triggered = True
                resume_count += 1
                retry_message = (
                    f"Resuming chunked screening attempt {attempt_index}/"
                    f"{_MAX_LOOP_ATTEMPTS}; {len(missing_indices)} studies remain."
                )
                logger.warning(
                    "%s review=%s gatekeeper=%s",
                    retry_message,
                    review_case.key,
                    gatekeeper_model.key,
                )
                agent_logger.log(retry_message)

            chunks = _chunk_indices(
                missing_indices,
                chunk_count=chunk_count,
                chunk_size=chunk_size,
            )
            for chunk_number, chunk in enumerate(chunks, start=1):
                try:
                    chunk_orchestrator = create_screening_chunk_loop_orchestrator_agent(
                        orchestrator_model.create_model(),
                        gatekeeper_model.create_model(),
                        step_callbacks=step_callbacks,
                        logger=agent_logger,
                    )
                    retry_note = None
                    if attempt_index > 1:
                        retry_note = (
                            "This is a resume attempt. Process only the listed "
                            "missing chunk indices and append exactly those decisions."
                        )
                    chunk_orchestrator.run(
                        _build_chunk_loop_screening_task(
                            review,
                            run_dir,
                            chunk_indices=chunk,
                            expected_n_studies=len(review.studies),
                            chunk_number=chunk_number,
                            chunk_total=len(chunks),
                            retry_note=retry_note,
                        )
                    )
                except Exception as attempt_exc:
                    last_attempt_error = f"{type(attempt_exc).__name__}: {attempt_exc}"
                    logger.warning(
                        "Chunked loop chunk failed: review=%s chunk=%s error=%s",
                        review_case.key,
                        chunk,
                        last_attempt_error,
                    )
                    break

            decisions = _read_screening_decisions(evidence_path)
            attempt_metrics = compute_screening_metrics(
                review,
                decisions,
                label_policy=label_policy,
            )
            if attempt_metrics["parse_success"]:
                break

        decisions = _read_screening_decisions(evidence_path)
        final_metrics = compute_screening_metrics(
            review,
            decisions,
            label_policy=label_policy,
        )
        if final_metrics["parse_success"]:
            run_status = "completed"
        elif last_attempt_error and final_metrics["screening_decision_count"] == 0:
            run_status = "error"
            error = last_attempt_error
        else:
            run_status = "incomplete"
            error = last_attempt_error
    finally:
        duration_seconds = time.perf_counter() - started_at
        activity_path = activity_logger.finalize(model=None)
        telemetry = collect_activity_telemetry(
            activity_logger,
            duration_seconds=duration_seconds,
            n_studies=len(review.studies),
            retry_count=max(screening_attempt_count - 1, 0),
            resume_count=resume_count,
        )
        telemetry["chunk_count"] = len(planned_chunks)
        telemetry["chunk_sizes"] = [len(chunk) for chunk in planned_chunks]
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
        "screening_attempt_count": screening_attempt_count,
        "rerun_triggered": rerun_triggered,
        "benchmark_architecture": benchmark_architecture,
        "telemetry": telemetry,
    }


def run_screening_loop_benchmark(
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
    loop_mode: str = "single-study",
    chunk_count: int | None = None,
    chunk_size: int | None = None,
    canonical_mode: str = "none",
) -> tuple[Path, dict]:
    """
    Run the looped Gatekeeper screening benchmark matrix.
    """
    if repeats < 1:
        raise ValueError("--repeats must be at least 1")
    if orchestrator_policy not in {"fixed", "match-gatekeeper"}:
        raise ValueError("--orchestrator-policy must be 'fixed' or 'match-gatekeeper'")
    if loop_mode not in {"single-study", "chunked"}:
        raise ValueError("--loop-mode must be 'single-study' or 'chunked'")
    if canonical_mode not in {"auto", "none", "force"}:
        raise ValueError("canonical_mode must be 'auto', 'none', or 'force'")
    if loop_mode != "chunked" and (chunk_count is not None or chunk_size is not None):
        raise ValueError("--chunk-count and --chunk-size require --loop-mode chunked")
    if chunk_count is not None and chunk_size is not None:
        raise ValueError("Use only one of --chunk-count or --chunk-size")
    selected_label_policies = list(SCREENING_LABEL_POLICIES)

    selected_reviews = resolve_review_selection(suite_name, review_keys)
    resolved_gatekeeper_models = resolve_model_presets(model_presets)
    fixed_orchestrator_model = get_model_preset(orchestrator_model_key).resolve()
    model_key_list = [model.key for model in resolved_gatekeeper_models]
    experiment_dir = _loop_experiment_root_for_mode(suite_name, model_key_list, loop_mode)
    benchmark_architecture = _loop_architecture_name(loop_mode)
    review_key_list = [review.key for review in selected_reviews]
    orchestrator_preset = (
        fixed_orchestrator_model.key
        if orchestrator_policy == "fixed"
        else "match-gatekeeper"
    )
    raw_runs_output_root = _raw_runs_checkpoint_root(experiment_dir)
    total_expected_raw_runs = (
        len(selected_reviews) * len(resolved_gatekeeper_models) * repeats
    )

    logger.info("Looped screening benchmark output dir: %s", experiment_dir)
    logger.info(
        "Running looped suite=%s mode=%s reviews=%d gatekeeper_models=%d repeats=%d policy=%s",
        suite_name,
        loop_mode,
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
                    "Loop benchmark run: mode=%s review=%s gatekeeper=%s orchestrator=%s repeat=%d/%d",
                    loop_mode,
                    review_case.key,
                    gatekeeper_model.key,
                    orchestrator_model.key,
                    run_index,
                    repeats,
                )
                review_runner = (
                    run_screening_chunk_loop_review
                    if loop_mode == "chunked"
                    else run_screening_loop_review
                )
                runner_kwargs = {}
                if loop_mode == "chunked":
                    runner_kwargs.update({
                        "chunk_count": chunk_count,
                        "chunk_size": chunk_size,
                    })
                raw_runs.append(
                    review_runner(
                        suite_name=suite_name,
                        review_case=review_case,
                        gatekeeper_model=gatekeeper_model,
                        orchestrator_model=orchestrator_model,
                        orchestrator_policy=orchestrator_policy,
                        run_index=run_index,
                        output_root=raw_runs_output_root,
                        label_policy="include_label_0_5",
                        include_subagent_steps=include_subagent_steps,
                        **runner_kwargs,
                    )
                )
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
                    benchmark_architecture=benchmark_architecture,
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
                        "loop_mode": loop_mode,
                        "chunk_count": chunk_count,
                        "chunk_size": chunk_size,
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
        benchmark_architecture=benchmark_architecture,
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
            "loop_mode": loop_mode,
            "chunk_count": chunk_count,
            "chunk_size": chunk_size,
        },
    )

    return experiment_dir, {
        "generated_at": datetime.now().isoformat(),
        "suite": suite_name,
        "benchmark_architecture": benchmark_architecture,
        "loop_mode": loop_mode,
        "chunk_count": chunk_count,
        "chunk_size": chunk_size,
        "repeats": repeats,
        "review_keys": review_key_list,
        "model_presets": model_key_list,
        "orchestrator_policy": orchestrator_policy,
        "orchestrator_preset": orchestrator_preset,
        "gold_label_policies": selected_label_policies,
        "raw_runs_dir": str(raw_runs_output_root),
        "checkpoint_manifest": str(experiment_dir / "benchmark_checkpoint.json"),
        "completed_raw_run_count": len(raw_runs),
        "total_expected_raw_runs": total_expected_raw_runs,
        "comparison_html_report": comparison_report,
        "policy_outputs": policy_summaries,
    }


def _load_loop_checkpoint_raw_runs(
    experiment_dir: Path,
    *,
    checkpoint: dict,
    label_policy: str,
) -> list[dict]:
    suite_name = checkpoint["suite"]
    policy_dir = _policy_dir_for_label(experiment_dir, label_policy)
    summary_path = policy_dir / "summary.json"
    if not summary_path.exists():
        raise FileNotFoundError(f"Expected policy summary at: {summary_path}")

    summary = _read_json(summary_path)
    metrics_by_run_id = {
        row["benchmark_run_id"]: row
        for row in summary.get("runs", [])
    }
    review_case_by_key = {
        review.key: review
        for review in resolve_review_selection(suite_name, checkpoint.get("review_keys") or None)
    }

    raw_runs: list[dict] = []
    for checkpoint_run in checkpoint.get("completed_runs", []):
        run_id = checkpoint_run["benchmark_run_id"]
        metrics = metrics_by_run_id.get(run_id)
        if metrics is None:
            raise ValueError(
                f"Checkpoint run '{run_id}' is missing from {summary_path}."
            )
        review_key = checkpoint_run["review_key"]
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
        raw_run_dir = Path(checkpoint_run["raw_run_dir"])
        evidence_path = raw_run_dir / "evidence.json"
        if not evidence_path.exists():
            raise FileNotFoundError(f"Expected raw evidence at: {evidence_path}")

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
            "raw_run_dir": raw_run_dir,
            "run_status": metrics.get("run_status", "completed"),
            "error": metrics.get("error", ""),
            "screening_attempt_count": int(metrics.get("screening_attempt_count", 1)),
            "rerun_triggered": bool(metrics.get("rerun_triggered", False)),
            "benchmark_architecture": metrics.get("benchmark_architecture", LOOP_BENCHMARK_ARCHITECTURE),
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


def rerun_screening_loop_reviews_in_experiment(
    *,
    experiment_dir: Path,
    review_keys: list[str],
    include_subagent_steps: bool = True,
    execute_policy_notebooks: bool = True,
) -> tuple[Path, dict]:
    """
    Rerun selected reviews inside an existing looped experiment and rematerialize summaries.
    """
    if not review_keys:
        raise ValueError("--reviews is required when using --rerun-in-experiment")

    experiment_dir = Path(experiment_dir)
    checkpoint_path = experiment_dir / "benchmark_checkpoint.json"
    if not checkpoint_path.exists():
        raise FileNotFoundError(f"Expected loop checkpoint at: {checkpoint_path}")
    checkpoint = _read_json(checkpoint_path)
    checkpoint_architecture = checkpoint.get("benchmark_architecture")
    if checkpoint_architecture not in {
        LOOP_BENCHMARK_ARCHITECTURE,
        LOOP_CHUNK_BENCHMARK_ARCHITECTURE,
    }:
        raise ValueError(
            f"Experiment is not a loop benchmark: {checkpoint_architecture}"
        )
    loop_mode = checkpoint.get("loop_mode")
    if not loop_mode:
        loop_mode = "chunked" if checkpoint_architecture == LOOP_CHUNK_BENCHMARK_ARCHITECTURE else "single-study"
    chunk_count = checkpoint.get("chunk_count")
    chunk_size = checkpoint.get("chunk_size")

    suite_name = checkpoint["suite"]
    original_review_keys = checkpoint.get("review_keys") or []
    original_model_keys = checkpoint.get("model_presets") or []
    selected_label_policies = list(SCREENING_LABEL_POLICIES)
    orchestrator_policy = checkpoint["orchestrator_policy"]
    orchestrator_preset = checkpoint["orchestrator_preset"]
    repeats = int(checkpoint.get("repeats", 1))

    unknown_review_keys = [key for key in review_keys if key not in original_review_keys]
    if unknown_review_keys:
        raise ValueError(
            "Cannot rerun review key(s) outside the original experiment: "
            + ", ".join(unknown_review_keys)
        )

    source_label_policy = selected_label_policies[0]
    raw_runs = _load_loop_checkpoint_raw_runs(
        experiment_dir,
        checkpoint=checkpoint,
        label_policy=source_label_policy,
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
                    "Rerunning loop benchmark review in existing experiment: mode=%s review=%s gatekeeper=%s orchestrator=%s repeat=%d/%d",
                    loop_mode,
                    review_case.key,
                    gatekeeper_model.key,
                    orchestrator_model.key,
                    run_index,
                    repeats,
                )
                review_runner = (
                    run_screening_chunk_loop_review
                    if loop_mode == "chunked"
                    else run_screening_loop_review
                )
                runner_kwargs = {}
                if loop_mode == "chunked":
                    runner_kwargs.update({
                        "chunk_count": chunk_count,
                        "chunk_size": chunk_size,
                    })
                raw_run = review_runner(
                    suite_name=suite_name,
                    review_case=review_case,
                    gatekeeper_model=gatekeeper_model,
                    orchestrator_model=orchestrator_model,
                    orchestrator_policy=orchestrator_policy,
                    run_index=run_index,
                    output_root=raw_runs_output_root,
                    label_policy="include_label_0_5",
                    include_subagent_steps=include_subagent_steps,
                    **runner_kwargs,
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
        benchmark_architecture=checkpoint_architecture,
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
            "loop_mode": loop_mode,
            "chunk_count": chunk_count,
            "chunk_size": chunk_size,
        },
    )

    return experiment_dir, {
        "generated_at": datetime.now().isoformat(),
        "suite": suite_name,
        "benchmark_architecture": checkpoint_architecture,
        "loop_mode": loop_mode,
        "chunk_count": chunk_count,
        "chunk_size": chunk_size,
        "repeats": repeats,
        "review_keys": original_review_keys,
        "rerun_review_keys": review_keys,
        "model_presets": original_model_keys,
        "orchestrator_policy": orchestrator_policy,
        "orchestrator_preset": orchestrator_preset,
        "gold_label_policies": selected_label_policies,
        "raw_runs_dir": str(raw_runs_output_root),
        "checkpoint_manifest": str(checkpoint_path),
        "completed_raw_run_count": len(merged_raw_runs),
        "total_expected_raw_runs": total_expected_raw_runs,
        "comparison_html_report": comparison_report,
        "policy_outputs": policy_summaries,
    }
