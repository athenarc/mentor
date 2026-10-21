"""
Path layout, JSON IO, and telemetry field lists for benchmark harness code.

Policy directory names map gold-label policies to ``include_policy`` /
``exclude_policy`` folders. ``resolve_existing_path`` rewrites legacy
benchmark paths to ``data/experiments/output/screening_benchmarks``.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments.paths import PROJECT_ROOT

POLICY_DIR_NAMES = {
    "include_label_0_5": "include_policy",
    "exclude_label_0_5": "exclude_policy",
}

_LEGACY_BENCHMARK_PREFIXES = (
    ("data", "experiments", "output", "screening_benchmarks"),
    ("data", "output", "screening_benchmarks"),
    ("mentor", "output", "screening_benchmarks"),
    ("bastirr", "output", "screening_benchmarks"),
    ("output", "screening_benchmarks"),
)

_METRIC_TELEMETRY_KEYS = (
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


def policy_dir_name(label_policy: str) -> str:
    return POLICY_DIR_NAMES.get(label_policy, label_policy)


def policy_dir_for_label(experiment_dir: Path, label_policy: str) -> Path:
    return experiment_dir / policy_dir_name(label_policy)


def read_json(path: Path) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def rewrite_legacy_benchmark_path(path: Path) -> Path:
    """Map legacy benchmark roots to data/experiments/output/screening_benchmarks/…."""
    parts = path.parts
    for prefix in _LEGACY_BENCHMARK_PREFIXES:
        prefix_len = len(prefix)
        for index in range(len(parts) - prefix_len + 1):
            if parts[index : index + prefix_len] == prefix:
                # Drop everything before "screening_benchmarks"; keep that suffix.
                suffix_start = index + prefix_len - 1
                return Path("data", "experiments", "output", *parts[suffix_start:])
    return path


def resolve_existing_path(path_value: str | Path) -> Path:
    path = Path(path_value)
    if path.exists():
        return path

    candidates: list[Path] = []
    rewritten = rewrite_legacy_benchmark_path(path)
    if rewritten != path:
        candidates.append(rewritten)
        candidates.append(PROJECT_ROOT / rewritten)
        # Preserve previous relative rewrites (mentor/output/…, output/…).
        parts = path.parts
        for prefix in _LEGACY_BENCHMARK_PREFIXES:
            prefix_len = len(prefix)
            for index in range(len(parts) - prefix_len + 1):
                if parts[index : index + prefix_len] == prefix:
                    candidates.append(Path(*parts[index:]))

    for candidate in candidates:
        if candidate.exists():
            return candidate
    return path


def metric_telemetry(metrics: dict) -> dict:
    return {key: metrics[key] for key in _METRIC_TELEMETRY_KEYS if key in metrics}


def sort_raw_runs(
    raw_runs: list[dict],
    *,
    review_keys: list[str],
    model_keys: list[str],
) -> list[dict]:
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
