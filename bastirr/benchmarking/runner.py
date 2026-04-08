"""
Core runner for the Gatekeeper screening benchmark harness.
"""

from __future__ import annotations

import csv
import json
import logging
import time
from datetime import datetime
from pathlib import Path
from statistics import fmean

from bastirr.agents.screening_orchestrator import create_screening_orchestrator_agent
from bastirr.benchmarking.inspection import write_screening_inspection_artifacts
from bastirr.benchmarking.metrics import compute_screening_metrics
from bastirr.benchmarking.model_presets import (
    ResolvedModelPreset,
    get_model_preset,
    resolve_model_presets,
)
from bastirr.benchmarking.review_suites import (
    ScreeningBenchmarkReview,
    resolve_review_selection,
)
from bastirr.config import OUTPUT_DIR
from bastirr.data import load_review
from bastirr.logging_utils import make_step_callbacks, setup_run_logging
from bastirr.run_demo import review_to_json
from bastirr.tools.search_tools import load_review_data

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
)
logger = logging.getLogger("bastirr.screening_benchmark")


_SUMMARY_CSV_PRIORITY_FIELDS = [
    "benchmark_run_id",
    "suite",
    "review_key",
    "review_title",
    "split",
    "n_studies",
    "run_index",
    "run_status",
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


def _build_screening_task(review, output_dir: Path) -> str:
    return (
        "Conduct only the title/abstract screening phase for this review.\n\n"
        f"Review title: {review.title}\n\n"
        f"Review background:\n{review.background}\n\n"
        f"Review objective:\n{review.objective}\n\n"
        f"Selection criteria:\n{review.selection_criteria}\n\n"
        f"Output directory: {output_dir}\n\n"
        "Execute the screening-only pipeline:\n"
        "1. Use get_candidates_json() to retrieve the preloaded candidate studies.\n"
        "2. Use the gatekeeper to screen all studies using the selection criteria verbatim.\n"
        "3. Use save_screening_evidence_json() to save evidence.json in the output directory.\n"
        "4. Use format_screening_summary() and return the summary as the final answer.\n"
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
    error: str = "",
) -> dict:
    metrics = compute_screening_metrics(
        review,
        screening_decisions,
        label_policy=label_policy,
    )
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
        "run_index": run_index,
        "run_status": run_status,
        "error": error,
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
    return metrics


def _write_metrics_json(run_dir: Path, metrics: dict) -> None:
    with open(run_dir / "metrics.json", "w", encoding="utf-8") as f:
        json.dump(metrics, f, ensure_ascii=False, indent=2)


def run_screening_review(
    *,
    suite_name: str,
    review_case: ScreeningBenchmarkReview,
    gatekeeper_model: ResolvedModelPreset,
    orchestrator_model: ResolvedModelPreset,
    orchestrator_policy: str,
    run_index: int,
    experiment_dir: Path,
    label_policy: str,
    include_subagent_steps: bool = True,
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
    load_review_data(review_to_json(review))

    run_dir, agent_logger, activity_logger = setup_run_logging(
        review.title,
        include_subagent_steps=include_subagent_steps,
        output_root=experiment_dir / "runs",
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

    activity_logger.mark_pipeline_start()
    started_at = time.perf_counter()
    try:
        screening_orchestrator = create_screening_orchestrator_agent(
            orchestrator_model.create_model(),
            gatekeeper_model.create_model(),
            step_callbacks=step_callbacks,
            logger=agent_logger,
        )
        screening_orchestrator.run(_build_screening_task(review, run_dir))
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
        logger.info("Activity log saved to: %s", activity_path)
        agent_logger.close()

    decisions = _read_screening_decisions(evidence_path)
    metrics = _build_run_metrics(
        review_case=review_case,
        review=review,
        screening_decisions=decisions,
        gatekeeper_model=gatekeeper_model,
        orchestrator_model=orchestrator_model,
        orchestrator_policy=orchestrator_policy,
        suite_name=suite_name,
        run_index=run_index,
        duration_seconds=duration_seconds,
        run_dir=run_dir,
        run_status=run_status,
        label_policy=label_policy,
        error=error,
    )
    metrics.update(
        write_screening_inspection_artifacts(
            run_dir=run_dir,
            review=review,
            screening_decisions=decisions,
            metrics=metrics,
        )
    )
    _write_metrics_json(run_dir, metrics)
    return metrics


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
    grouped: dict[tuple[str, str, str, str, str, str, str], list[dict]] = {}
    for row in run_metrics:
        key = (
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
        gatekeeper_model_label,
        gatekeeper_backend,
        gatekeeper_api_base,
        orchestrator_policy,
        orchestrator_model_label,
        orchestrator_backend,
        orchestrator_api_base,
    ), rows in grouped.items():
        completed_rows = [row for row in rows if row.get("run_status") == "completed"]
        aggregates.append({
            "gold_label_policy": rows[0]["gold_label_policy"],
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
            "n_completed_runs": len(completed_rows),
            "n_failed_runs": len(rows) - len(completed_rows),
            "n_unique_reviews": len({row["review_key"] for row in rows}),
            "parse_success_rate": _mean_for(
                [{"value": 1.0 if row.get("parse_success") else 0.0} for row in rows],
                "value",
            ),
            "mean_decision_coverage": _mean_for(rows, "decision_coverage"),
            "mean_accuracy": _mean_for(completed_rows, "accuracy"),
            "mean_precision": _mean_for(completed_rows, "precision"),
            "mean_recall": _mean_for(completed_rows, "recall"),
            "mean_specificity": _mean_for(completed_rows, "specificity"),
            "mean_f1": _mean_for(completed_rows, "f1"),
            "mean_duration_seconds": _mean_for(rows, "duration_seconds"),
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
    grouped: dict[tuple[str, str, str, int, int, int, str, str, str, str, str, str], list[dict]] = {}
    for row in run_metrics:
        key = (
            row["review_key"],
            row["review_title"],
            row["review_url"],
            row["n_studies"],
            row["gold_pass_count"],
            row["gold_exclude_count"],
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
        gatekeeper_model_label,
        gatekeeper_backend,
        gatekeeper_api_base,
        orchestrator_policy,
        orchestrator_model_label,
        orchestrator_api_base,
    ), rows in grouped.items():
        completed_rows = [row for row in rows if row.get("run_status") == "completed"]
        aggregates.append({
            "gold_label_policy": rows[0]["gold_label_policy"],
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
            "n_completed_runs": len(completed_rows),
            "n_failed_runs": len(rows) - len(completed_rows),
            "parse_success_rate": _mean_for(
                [{"value": 1.0 if row.get("parse_success") else 0.0} for row in rows],
                "value",
            ),
            "mean_decision_coverage": _mean_for(rows, "decision_coverage"),
            "mean_accuracy": _mean_for(completed_rows, "accuracy"),
            "mean_precision": _mean_for(completed_rows, "precision"),
            "mean_recall": _mean_for(completed_rows, "recall"),
            "mean_specificity": _mean_for(completed_rows, "specificity"),
            "mean_f1": _mean_for(completed_rows, "f1"),
            "mean_duration_seconds": _mean_for(rows, "duration_seconds"),
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
    with open(experiment_dir / "summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    return summary


def _write_summary_csv(experiment_dir: Path, run_metrics: list[dict]) -> None:
    if not run_metrics:
        return
    seen = set()
    fieldnames: list[str] = []
    for field in _SUMMARY_CSV_PRIORITY_FIELDS:
        if field in run_metrics[0] and field not in seen:
            fieldnames.append(field)
            seen.add(field)
    for field in run_metrics[0]:
        if field not in seen:
            fieldnames.append(field)
            seen.add(field)
    with open(experiment_dir / "summary.csv", "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(run_metrics)


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
        "| Rank | Gatekeeper Model | Orchestrator Policy | Orchestrator Model | Runs | F1 | Recall | Precision | Accuracy | Specificity | Parse Success | Coverage |",
        "|------|------------------|---------------------|--------------------|------|----|--------|-----------|----------|-------------|---------------|----------|",
    ]

    for rank, row in enumerate(aggregates, start=1):
        lines.append(
            "| {rank} | {gatekeeper} | {policy} | {orchestrator} | {runs} | {f1} | {recall} | {precision} | {accuracy} | {specificity} | {parse_success} | {coverage} |".format(
                rank=rank,
                gatekeeper=row["gatekeeper_model_label"],
                policy=row["orchestrator_policy"],
                orchestrator=row["orchestrator_model_label"],
                runs=row["n_runs"],
                f1=_format_metric(row["mean_f1"]),
                recall=_format_metric(row["mean_recall"]),
                precision=_format_metric(row["mean_precision"]),
                accuracy=_format_metric(row["mean_accuracy"]),
                specificity=_format_metric(row["mean_specificity"]),
                parse_success=_format_metric(row["parse_success_rate"]),
                coverage=_format_metric(row["mean_decision_coverage"]),
            )
        )

    with open(experiment_dir / "leaderboard.md", "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


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
                "| Rank | Gatekeeper Model | Orchestrator Policy | Orchestrator Model | Runs | F1 | Recall | Precision | Accuracy | Specificity | Parse Success | Coverage |",
                "|------|------------------|---------------------|--------------------|------|----|--------|-----------|----------|-------------|---------------|----------|",
            ])
            for rank, row in enumerate(sorted_rows, start=1):
                lines.append(
                    "| {rank} | {gatekeeper} | {policy} | {orchestrator} | {runs} | {f1} | {recall} | {precision} | {accuracy} | {specificity} | {parse_success} | {coverage} |".format(
                        rank=rank,
                        gatekeeper=row["gatekeeper_model_label"],
                        policy=row["orchestrator_policy"],
                        orchestrator=row["orchestrator_model_label"],
                        runs=row["n_runs"],
                        f1=_format_metric(row["mean_f1"]),
                        recall=_format_metric(row["mean_recall"]),
                        precision=_format_metric(row["mean_precision"]),
                        accuracy=_format_metric(row["mean_accuracy"]),
                        specificity=_format_metric(row["mean_specificity"]),
                        parse_success=_format_metric(row["parse_success_rate"]),
                        coverage=_format_metric(row["mean_decision_coverage"]),
                    )
                )

    with open(experiment_dir / "review_leaderboard.md", "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def run_screening_benchmark(
    *,
    suite_name: str = "screening_ladder",
    model_presets: list[str] | None = None,
    repeats: int = 1,
    orchestrator_policy: str = "fixed",
    orchestrator_model_key: str = "openai_gpt5",
    review_keys: list[str] | None = None,
    gold_label_policy: str = "include_label_0_5",
    include_subagent_steps: bool = True,
) -> tuple[Path, dict]:
    """
    Run the Gatekeeper screening benchmark matrix and write experiment summaries.
    """
    if repeats < 1:
        raise ValueError("--repeats must be at least 1")
    if orchestrator_policy not in {"fixed", "match-gatekeeper"}:
        raise ValueError("--orchestrator-policy must be 'fixed' or 'match-gatekeeper'")

    selected_reviews = resolve_review_selection(suite_name, review_keys)
    resolved_gatekeeper_models = resolve_model_presets(model_presets)
    fixed_orchestrator_model = get_model_preset(orchestrator_model_key).resolve()
    experiment_dir = _experiment_root(suite_name)

    logger.info("Screening benchmark output dir: %s", experiment_dir)
    logger.info(
        "Running suite=%s reviews=%d gatekeeper_models=%d repeats=%d policy=%s",
        suite_name,
        len(selected_reviews),
        len(resolved_gatekeeper_models),
        repeats,
        orchestrator_policy,
    )

    run_metrics: list[dict] = []
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
                metrics = run_screening_review(
                    suite_name=suite_name,
                    review_case=review_case,
                    gatekeeper_model=gatekeeper_model,
                    orchestrator_model=orchestrator_model,
                    orchestrator_policy=orchestrator_policy,
                    run_index=run_index,
                    experiment_dir=experiment_dir,
                    label_policy=gold_label_policy,
                    include_subagent_steps=include_subagent_steps,
                )
                run_metrics.append(metrics)

    aggregates = _aggregate_runs(run_metrics)
    review_aggregates = _aggregate_runs_by_review(run_metrics)
    summary = _write_summary_json(
        experiment_dir,
        suite_name=suite_name,
        repeats=repeats,
        review_keys=[review.key for review in selected_reviews],
        model_presets=[model.key for model in resolved_gatekeeper_models],
        orchestrator_policy=orchestrator_policy,
        orchestrator_preset=(
            fixed_orchestrator_model.key
            if orchestrator_policy == "fixed"
            else "match-gatekeeper"
        ),
        gold_label_policy=gold_label_policy,
        run_metrics=run_metrics,
        aggregates=aggregates,
        review_aggregates=review_aggregates,
    )
    _write_summary_csv(experiment_dir, run_metrics)
    _write_leaderboard_markdown(experiment_dir, aggregates)
    _write_review_leaderboard_markdown(experiment_dir, review_aggregates)
    return experiment_dir, summary
