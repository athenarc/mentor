"""
Aggregate screening benchmark outputs across experiment directories.
"""

from __future__ import annotations

import json
import re
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from statistics import fmean
from typing import Iterable

from bastirr.config import OUTPUT_DIR, PROJECT_ROOT
from bastirr.benchmarking.model_presets import get_model_preset


BATCH_ARCHITECTURE = "batch_orchestrator_v1"
CANONICAL_SOURCES_FILENAME = "canonical_sources.json"
CANONICAL_SOURCES_AUDIT_JSON_FILENAME = "canonical_sources_audit.json"
CANONICAL_SOURCES_AUDIT_MD_FILENAME = "canonical_sources_audit.md"
CANONICAL_AUDIT_DIRNAME = "_archive"
DEFAULT_CANONICAL_POLICY = "exclude_label_0_5"
DEFAULT_CANONICAL_GOLD_LABEL_POLICIES = (DEFAULT_CANONICAL_POLICY,)
SOURCE_MODES = ("canonical", "discover", "all")
SIZE_BANDS = (
    {
        "key": "small_10",
        "label": "up to 15",
        "min_studies": None,
        "max_studies": 15,
    },
    {
        "key": "lower_mid_25",
        "label": "16-35",
        "min_studies": 16,
        "max_studies": 35,
    },
    {
        "key": "mid_50",
        "label": "36-65",
        "min_studies": 36,
        "max_studies": 65,
    },
    {
        "key": "upper_mid_100",
        "label": "66-100",
        "min_studies": 66,
        "max_studies": 100,
    },
    {
        "key": "large_100_plus",
        "label": "100+",
        "min_studies": 101,
        "max_studies": None,
    },
)

_POLICY_DIR_NAMES = {
    "include_label_0_5": "include_policy",
    "exclude_label_0_5": "exclude_policy",
}


def _policy_dir_name(label_policy: str) -> str:
    return _POLICY_DIR_NAMES.get(label_policy, label_policy)


def _repo_relative_path(path: Path | str) -> str:
    """Return a path relative to the project root when possible."""
    resolved = Path(path).resolve()
    try:
        return str(resolved.relative_to(PROJECT_ROOT))
    except ValueError:
        return str(resolved)


def _resolve_repo_path(path: Path | str) -> Path:
    candidate = Path(path)
    if candidate.is_absolute():
        return candidate
    return PROJECT_ROOT / candidate


def _as_float(value) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _as_int(value) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def _canonical_model_label(preset_key: str, fallback: str = "") -> str:
    if not preset_key:
        return fallback
    try:
        return get_model_preset(preset_key).resolve(strict=False).model_label
    except Exception:
        return fallback or preset_key


def _source_timestamp(summary_path: Path, summary: dict) -> str:
    generated_at = str(summary.get("generated_at", ""))
    experiment_name = summary_path.parent.parent.name
    match = re.match(r"(\d{8}_\d{6})", experiment_name)
    experiment_stamp = match.group(1) if match else ""
    return f"{generated_at}|{experiment_stamp}"


def _mean_for(rows: Iterable[dict], key: str) -> float | None:
    values = [
        value
        for value in (_as_float(row.get(key)) for row in rows)
        if value is not None
    ]
    if not values:
        return None
    return fmean(values)


def _format_metric(value: float | None) -> str:
    return "n/a" if value is None else f"{value:.3f}"


def size_band_for(n_studies: int) -> dict:
    """Return the configured size band for a review study count."""
    for band in SIZE_BANDS:
        lower = band["min_studies"]
        upper = band["max_studies"]
        if lower is not None and n_studies < lower:
            continue
        if upper is not None and n_studies > upper:
            continue
        return band
    return SIZE_BANDS[-1]


def _summary_paths(output_root: Path) -> list[Path]:
    totals_root = output_root / "totals"
    paths = []
    for path in output_root.glob("*/*/summary.json"):
        try:
            path.relative_to(totals_root)
            continue
        except ValueError:
            pass
        paths.append(path)
    return sorted(paths)


def _load_policy_runs(summary_path: Path) -> list[dict]:
    with open(summary_path, "r", encoding="utf-8") as f:
        summary = json.load(f)
    runs = summary.get("runs", [])
    if not isinstance(runs, list):
        return []
    summary_repeats = _as_int(summary.get("repeats")) or 1
    summary_review_keys = [
        str(review_key)
        for review_key in (summary.get("review_keys") or [])
        if str(review_key)
    ]
    if not summary_review_keys:
        summary_review_keys = sorted({
            str(row.get("review_key", ""))
            for row in runs
            if isinstance(row, dict) and str(row.get("review_key", ""))
        })
    loaded = []
    for row in runs:
        if not isinstance(row, dict):
            continue
        normalized = dict(row)
        normalized.setdefault("suite", summary.get("suite", ""))
        normalized.setdefault("gold_label_policy", summary.get("gold_label_policy", ""))
        normalized.setdefault("benchmark_architecture", BATCH_ARCHITECTURE)
        normalized["_summary_repeats"] = summary_repeats
        normalized["_summary_review_keys"] = summary_review_keys
        normalized["_source_timestamp"] = _source_timestamp(summary_path, summary)
        normalized["source_summary_json"] = _repo_relative_path(summary_path)
        normalized["source_experiment_dir"] = _repo_relative_path(summary_path.parent.parent)
        normalized["gatekeeper_model_label"] = _canonical_model_label(
            normalized.get("gatekeeper_preset", ""),
            normalized.get("gatekeeper_model_label", ""),
        )
        normalized["orchestrator_model_label"] = _canonical_model_label(
            normalized.get("orchestrator_preset", ""),
            normalized.get("orchestrator_model_label", ""),
        )
        loaded.append(normalized)
    return loaded


def _model_variant_key(row: dict) -> tuple:
    return (
        row.get("benchmark_architecture", BATCH_ARCHITECTURE),
        row.get("gatekeeper_preset", ""),
        row.get("orchestrator_policy", ""),
        row.get("orchestrator_preset", ""),
    )


def _canonical_row_key(row: dict, *, separate_suites: bool = True) -> tuple:
    suite_key = (row.get("suite", ""),) if separate_suites else ()
    return (
        *suite_key,
        row.get("gold_label_policy", ""),
        row.get("review_key", ""),
        *_model_variant_key(row),
        _as_int(row.get("run_index")),
    )


def _canonical_entry_key(entry: dict, *, separate_suites: bool = True) -> tuple:
    suite_key = (entry.get("suite", ""),) if separate_suites else ()
    return (
        *suite_key,
        entry.get("gold_label_policy", ""),
        entry.get("review_key", ""),
        entry.get("benchmark_architecture", BATCH_ARCHITECTURE),
        entry.get("gatekeeper_preset", ""),
        entry.get("orchestrator_policy", ""),
        entry.get("orchestrator_preset", ""),
        _as_int(entry.get("run_index")),
    )


def _canonical_registry_key(row_or_entry: dict) -> tuple:
    return (
        row_or_entry.get("suite", ""),
        row_or_entry.get("gold_label_policy", ""),
        row_or_entry.get("benchmark_architecture", BATCH_ARCHITECTURE),
        row_or_entry.get("review_key", ""),
        row_or_entry.get("gatekeeper_preset", ""),
        row_or_entry.get("orchestrator_policy", ""),
        row_or_entry.get("orchestrator_preset", ""),
    )


def _model_group_key(row: dict) -> tuple:
    return (
        *_model_variant_key(row),
        row.get("gatekeeper_model_label", ""),
        row.get("orchestrator_model_label", ""),
    )


def _dedupe_latest_model_review_runs(
    rows: list[dict],
    *,
    separate_suites: bool = True,
) -> list[dict]:
    grouped: dict[tuple, list[dict]] = defaultdict(list)
    for row in rows:
        suite_key = (row.get("suite", ""),) if separate_suites else ()
        grouped[(
            *suite_key,
            row.get("gold_label_policy", ""),
            row.get("review_key", ""),
            *_model_variant_key(row),
        )].append(row)

    deduped = []
    for group_rows in grouped.values():
        selected = sorted(
            group_rows,
            key=lambda row: (
                1 if _as_int(row.get("_summary_repeats")) == 1 else 0,
                str(row.get("_source_timestamp", "")),
                _as_int(row.get("run_index")),
            ),
            reverse=True,
        )[0]
        if len(group_rows) > 1:
            selected = dict(selected)
            selected["deduplicated_from_n"] = len(group_rows)
            selected["deduplication_rule"] = (
                "same policy/review/architecture/model variant"
                + ("/suite; " if separate_suites else " across suites; ")
                + "prefer repeat=1 summaries, then most recent source timestamp"
            )
        deduped.append(selected)
    return deduped


def _canonical_manifest_path(totals_root: Path | None = None) -> Path:
    output_root = OUTPUT_DIR / "screening_benchmarks"
    root = totals_root or (output_root / "totals")
    return root / CANONICAL_SOURCES_FILENAME


def _source_experiment_name(row_or_entry: dict) -> str:
    source_dir = row_or_entry.get("source_experiment_dir", "")
    if not source_dir:
        source_json = row_or_entry.get("source_summary_json", "")
        return Path(source_json).parent.parent.name if source_json else ""
    return Path(source_dir).name


def _is_repetition_source(row_or_entry: dict) -> bool:
    experiment_name = _source_experiment_name(row_or_entry)
    return bool(re.search(r"(?:^|[_-])rep\d+(?:$|[_-])", experiment_name))


def _canonical_source_entry(row: dict, *, selection_reason: str) -> dict:
    return {
        "suite": row.get("suite", ""),
        "gold_label_policy": row.get("gold_label_policy", ""),
        "benchmark_architecture": row.get("benchmark_architecture", BATCH_ARCHITECTURE),
        "review_key": row.get("review_key", ""),
        "review_title": row.get("review_title", ""),
        "n_studies": _as_int(row.get("n_studies")),
        "gatekeeper_preset": row.get("gatekeeper_preset", ""),
        "gatekeeper_model_label": row.get("gatekeeper_model_label", ""),
        "orchestrator_policy": row.get("orchestrator_policy", ""),
        "orchestrator_preset": row.get("orchestrator_preset", ""),
        "orchestrator_model_label": row.get("orchestrator_model_label", ""),
        "run_index": _as_int(row.get("run_index")),
        "run_status": row.get("run_status", ""),
        "scored_for_aggregate": bool(row.get("scored_for_aggregate")),
        "source_repeats": _as_int(row.get("_summary_repeats")) or 1,
        "source_timestamp": row.get("_source_timestamp", ""),
        "source_summary_json": row.get("source_summary_json", ""),
        "source_experiment_dir": row.get("source_experiment_dir", ""),
        "selection_reason": selection_reason,
    }


def _read_canonical_manifest(path: Path) -> dict:
    if not path.exists():
        return {"version": 1, "sources": []}
    with open(path, "r", encoding="utf-8") as f:
        payload = json.load(f)
    if not isinstance(payload, dict):
        raise ValueError(f"Canonical source manifest must be a JSON object: {path}")
    sources = payload.get("sources", [])
    if not isinstance(sources, list):
        raise ValueError(f"Canonical source manifest has non-list sources: {path}")
    payload.setdefault("version", 1)
    payload["sources"] = sources
    return payload


def _write_canonical_manifest(path: Path, payload: dict) -> dict:
    payload = dict(payload)
    payload.pop("canonical_sources_audit_json_path", None)
    payload.pop("canonical_sources_audit_md_path", None)
    payload["generated_at"] = datetime.now().isoformat()
    payload["sources"] = sorted(
        payload.get("sources", []),
        key=lambda entry: (
            entry.get("suite", ""),
            entry.get("gold_label_policy", ""),
            entry.get("benchmark_architecture", ""),
            entry.get("review_key", ""),
            entry.get("gatekeeper_preset", ""),
            entry.get("orchestrator_policy", ""),
            entry.get("orchestrator_preset", ""),
        ),
    )
    _write_json(path, payload)
    return payload


def _canonical_audit_groups(sources: list[dict]) -> list[dict]:
    grouped: dict[tuple, list[dict]] = defaultdict(list)
    for source in sources:
        grouped[(
            source.get("suite", ""),
            source.get("gold_label_policy", ""),
            source.get("benchmark_architecture", ""),
            source.get("gatekeeper_preset", ""),
            source.get("gatekeeper_model_label", ""),
            _source_experiment_name(source),
            source.get("source_experiment_dir", ""),
            source.get("source_summary_json", ""),
        )].append(source)

    groups = []
    for key, group_sources in grouped.items():
        (
            suite,
            gold_label_policy,
            architecture,
            gatekeeper_preset,
            gatekeeper_model_label,
            source_experiment,
            source_experiment_dir,
            source_summary_json,
        ) = key
        review_keys = sorted({source.get("review_key", "") for source in group_sources})
        groups.append({
            "suite": suite,
            "gold_label_policy": gold_label_policy,
            "benchmark_architecture": architecture,
            "gatekeeper_preset": gatekeeper_preset,
            "gatekeeper_model_label": gatekeeper_model_label,
            "source_experiment": source_experiment,
            "source_experiment_dir": source_experiment_dir,
            "source_summary_json": source_summary_json,
            "n_reviews": len(review_keys),
            "review_keys": review_keys,
        })

    groups.sort(
        key=lambda group: (
            group["suite"],
            group["gold_label_policy"],
            group["benchmark_architecture"],
            group["gatekeeper_preset"],
            group["source_experiment"],
        )
    )
    return groups


def _write_canonical_audit_files(
    totals_root: Path,
    manifest: dict,
    *,
    excluded_repetition_sources: list[dict],
) -> None:
    groups = _canonical_audit_groups(manifest.get("sources", []))
    payload = {
        "generated_at": datetime.now().isoformat(),
        "canonical_sources_path": manifest.get("canonical_sources_path", ""),
        "canonical_gold_label_policies": manifest.get("canonical_gold_label_policies", []),
        "n_sources": len(manifest.get("sources", [])),
        "n_groups": len(groups),
        "n_excluded_repetition_sources": len(excluded_repetition_sources),
        "groups": groups,
        "excluded_repetition_sources": sorted(
            excluded_repetition_sources,
            key=lambda source: (
                source.get("suite", ""),
                source.get("gold_label_policy", ""),
                source.get("benchmark_architecture", ""),
                source.get("gatekeeper_preset", ""),
                source.get("review_key", ""),
                source.get("source_experiment_dir", ""),
            ),
        ),
    }
    audit_root = totals_root / CANONICAL_AUDIT_DIRNAME
    _write_json(audit_root / CANONICAL_SOURCES_AUDIT_JSON_FILENAME, payload)

    lines = [
        "# Canonical Sources Audit",
        "",
        f"Manifest: `{manifest.get('canonical_sources_path', '')}`",
        f"Canonical policies: {', '.join(manifest.get('canonical_gold_label_policies', [])) or 'none'}",
        f"Canonical sources: {payload['n_sources']}",
        f"Grouped source selections: {payload['n_groups']}",
        f"Excluded `_repN` sources: {payload['n_excluded_repetition_sources']}",
        "",
        "| Suite | Policy | Architecture | Gatekeeper Preset | Gatekeeper Model | Selected Source Experiment | Reviews | Review Keys |",
        "|-------|--------|--------------|-------------------|------------------|----------------------------|---------|-------------|",
    ]
    for group in groups:
        lines.append(
            "| {suite} | {policy} | {architecture} | {preset} | {model} | {source} | {n_reviews} | {reviews} |".format(
                suite=group["suite"],
                policy=group["gold_label_policy"],
                architecture=group["benchmark_architecture"],
                preset=group["gatekeeper_preset"],
                model=group["gatekeeper_model_label"],
                source=group["source_experiment"],
                n_reviews=group["n_reviews"],
                reviews=", ".join(group["review_keys"]),
            )
        )
    if excluded_repetition_sources:
        excluded_groups = _canonical_audit_groups(excluded_repetition_sources)
        lines.extend([
            "",
            "## Excluded `_repN` Sources",
            "",
            "| Suite | Policy | Architecture | Gatekeeper Preset | Source Experiment | Reviews | Review Keys |",
            "|-------|--------|--------------|-------------------|-------------------|---------|-------------|",
        ])
        for group in excluded_groups:
            lines.append(
                "| {suite} | {policy} | {architecture} | {preset} | {source} | {n_reviews} | {reviews} |".format(
                    suite=group["suite"],
                    policy=group["gold_label_policy"],
                    architecture=group["benchmark_architecture"],
                    preset=group["gatekeeper_preset"],
                    source=group["source_experiment"],
                    n_reviews=group["n_reviews"],
                    reviews=", ".join(group["review_keys"]),
                )
            )
    (audit_root / CANONICAL_SOURCES_AUDIT_MD_FILENAME).write_text(
        "\n".join(lines) + "\n",
        encoding="utf-8",
    )


def _eligible_canonical_rows(
    rows: list[dict],
    *,
    include_repeated: bool,
    include_repetition_folders: bool = True,
    gold_label_policies: Iterable[str] | None = DEFAULT_CANONICAL_GOLD_LABEL_POLICIES,
) -> list[dict]:
    policy_set = set(gold_label_policies or [])
    return [
        row
        for row in rows
        if row.get("run_status") == "completed"
        and bool(row.get("scored_for_aggregate"))
        and (not policy_set or row.get("gold_label_policy") in policy_set)
        and (include_repeated or (_as_int(row.get("_summary_repeats")) or 1) == 1)
        and (include_repetition_folders or not _is_repetition_source(row))
    ]


def write_canonical_sources(
    *,
    output_root: Path | None = None,
    totals_root: Path | None = None,
    include_repeated: bool = False,
    include_repetition_folders: bool = False,
    gold_label_policies: Iterable[str] | None = DEFAULT_CANONICAL_GOLD_LABEL_POLICIES,
) -> dict:
    """
    Build an explicit canonical source manifest from discovered summaries.

    This writes only ``canonical_sources.json``. It does not regenerate aggregate
    leaderboards.
    """
    output_root = output_root or (OUTPUT_DIR / "screening_benchmarks")
    totals_root = totals_root or (output_root / "totals")
    canonical_gold_label_policies = tuple(gold_label_policies or ())
    all_runs: list[dict] = []
    for summary_path in _summary_paths(output_root):
        all_runs.extend(_load_policy_runs(summary_path))

    pre_repetition_filter_rows = _eligible_canonical_rows(
        all_runs,
        include_repeated=include_repeated,
        include_repetition_folders=True,
        gold_label_policies=canonical_gold_label_policies,
    )
    excluded_repetition_rows = [
        row
        for row in pre_repetition_filter_rows
        if not include_repetition_folders and _is_repetition_source(row)
    ]
    eligible_rows = _eligible_canonical_rows(
        all_runs,
        include_repeated=include_repeated,
        include_repetition_folders=include_repetition_folders,
        gold_label_policies=canonical_gold_label_policies,
    )
    selected_rows = _dedupe_latest_model_review_runs(eligible_rows)
    excluded_repetition_sources = [
        _canonical_source_entry(
            row,
            selection_reason="excluded because source experiment folder is marked as repetition",
        )
        for row in excluded_repetition_rows
    ]
    payload = {
        "version": 1,
        "selection_mode": "discovered_latest_repeat1" if not include_repeated else "discovered_latest",
        "canonical_sources_path": _repo_relative_path(totals_root / CANONICAL_SOURCES_FILENAME),
        "canonical_gold_label_policies": list(canonical_gold_label_policies),
        "selection_rules": [
            "completed and scored runs only",
            "exclude-label policy only" if canonical_gold_label_policies == ("exclude_label_0_5",) else "explicit canonical gold-label policy filter",
            "provider/API base is ignored",
            "one entry per suite/policy/review/architecture/model variant",
            "repeat=1 summaries only" if not include_repeated else "repeated summaries allowed",
            "`_repN` experiment folders are excluded" if not include_repetition_folders else "`_repN` experiment folders are allowed",
            "newest source timestamp wins within duplicates",
        ],
        "n_discovered_runs": len(all_runs),
        "n_completed_scored_repeat_eligible_runs": len(pre_repetition_filter_rows),
        "n_excluded_repetition_folder_runs": len(excluded_repetition_rows),
        "n_eligible_runs": len(eligible_rows),
        "n_sources": len(selected_rows),
        "sources": [
            _canonical_source_entry(
                row,
                selection_reason="seeded from discovered summaries",
            )
            for row in selected_rows
        ],
    }
    written = _write_canonical_manifest(
        totals_root / CANONICAL_SOURCES_FILENAME,
        payload,
    )
    _write_canonical_audit_files(
        totals_root,
        written,
        excluded_repetition_sources=excluded_repetition_sources,
    )
    return written


def _load_runs_from_canonical_sources(*, totals_root: Path) -> list[dict]:
    manifest_path = totals_root / CANONICAL_SOURCES_FILENAME
    manifest = _read_canonical_manifest(manifest_path)
    loaded_by_summary: dict[str, list[dict]] = {}
    selected_rows = []
    missing_entries = []

    for entry in manifest.get("sources", []):
        summary_json = entry.get("source_summary_json") or entry.get("summary_json")
        if not summary_json:
            missing_entries.append({**entry, "missing_reason": "missing source_summary_json"})
            continue
        summary_path = _resolve_repo_path(summary_json)
        if not summary_path.exists():
            missing_entries.append({**entry, "missing_reason": f"summary not found: {summary_json}"})
            continue
        cache_key = str(summary_path)
        if cache_key not in loaded_by_summary:
            loaded_by_summary[cache_key] = _load_policy_runs(summary_path)
        entry_key = _canonical_entry_key(entry)
        matches = [
            row
            for row in loaded_by_summary[cache_key]
            if _canonical_row_key(row) == entry_key
        ]
        if not matches:
            missing_entries.append({**entry, "missing_reason": "matching run not found in summary"})
            continue
        selected = dict(matches[0])
        selected["canonical_source"] = True
        selected["canonical_selection_reason"] = entry.get("selection_reason", "")
        selected_rows.append(selected)

    if missing_entries:
        preview = "; ".join(
            f"{entry.get('review_key', '?')}:{entry.get('gatekeeper_preset', '?')} ({entry.get('missing_reason', '')})"
            for entry in missing_entries[:5]
        )
        raise ValueError(
            f"{len(missing_entries)} canonical source entries could not be resolved from "
            f"{_repo_relative_path(manifest_path)}: {preview}"
        )
    return selected_rows


def register_canonical_sources_from_experiment(
    experiment_dir: Path | str,
    *,
    totals_root: Path | None = None,
    mode: str = "auto",
    gold_label_policies: Iterable[str] | None = DEFAULT_CANONICAL_GOLD_LABEL_POLICIES,
) -> dict:
    """
    Add or replace canonical source entries from one completed experiment.

    ``mode='auto'`` registers only repeat=1 completed/scored runs.
    ``mode='force'`` also allows repeated summaries.
    ``mode='none'`` leaves the manifest unchanged.
    """
    if mode == "none":
        return {"registered_sources": 0, "canonical_sources": 0}
    if mode not in {"auto", "force"}:
        raise ValueError(f"Unknown canonical registration mode: {mode}")

    experiment_dir = Path(experiment_dir)
    canonical_gold_label_policies = tuple(gold_label_policies or ())
    output_root = OUTPUT_DIR / "screening_benchmarks"
    totals_root = totals_root or (output_root / "totals")
    manifest_path = totals_root / CANONICAL_SOURCES_FILENAME
    manifest = _read_canonical_manifest(manifest_path)
    by_key = {
        _canonical_registry_key(entry): entry
        for entry in manifest.get("sources", [])
    }

    include_repeated = mode == "force"
    candidate_rows: list[dict] = []
    for summary_path in sorted(experiment_dir.glob("*/summary.json")):
        candidate_rows.extend(_load_policy_runs(summary_path))
    pre_repetition_filter_rows = _eligible_canonical_rows(
        candidate_rows,
        include_repeated=include_repeated,
        include_repetition_folders=True,
        gold_label_policies=canonical_gold_label_policies,
    )
    excluded_repetition_rows = [
        row
        for row in pre_repetition_filter_rows
        if mode != "force" and _is_repetition_source(row)
    ]
    candidate_rows = _eligible_canonical_rows(
        candidate_rows,
        include_repeated=include_repeated,
        include_repetition_folders=mode == "force",
        gold_label_policies=canonical_gold_label_policies,
    )
    selected_rows = _dedupe_latest_model_review_runs(candidate_rows)
    for row in selected_rows:
        by_key[_canonical_registry_key(row)] = _canonical_source_entry(
            row,
            selection_reason=f"registered from benchmark run with canonical mode {mode}",
        )

    payload = {
        **manifest,
        "version": 1,
        "selection_mode": "explicit_manifest",
        "selection_rules": [
            "new benchmark runs replace the same suite/policy/review/architecture/model variant",
            "auto mode registers repeat=1 completed/scored runs only",
            "force mode can register repeated completed/scored runs",
            "canonical registration defaults to exclude-label policy only",
        ],
        "canonical_gold_label_policies": list(canonical_gold_label_policies),
        "sources": list(by_key.values()),
    }
    written = _write_canonical_manifest(manifest_path, payload)
    _write_canonical_audit_files(
        totals_root,
        written,
        excluded_repetition_sources=[
            _canonical_source_entry(
                row,
                selection_reason="excluded because source experiment folder is marked as repetition",
            )
            for row in excluded_repetition_rows
        ],
    )
    return {
        "canonical_sources_path": _repo_relative_path(manifest_path),
        "registered_sources": len(selected_rows),
        "excluded_repetition_folder_runs": len(excluded_repetition_rows),
        "canonical_sources": len(written.get("sources", [])),
    }


def _aggregate_model_rows(rows: list[dict]) -> list[dict]:
    grouped: dict[tuple, list[dict]] = defaultdict(list)
    for row in rows:
        grouped[_model_group_key(row)].append(row)

    aggregates = []
    for key, group_rows in grouped.items():
        scored_rows = [row for row in group_rows if bool(row.get("scored_for_aggregate"))]
        (
            architecture,
            gatekeeper_preset,
            orchestrator_policy,
            orchestrator_preset,
            gatekeeper_model_label,
            orchestrator_model_label,
        ) = key
        aggregates.append({
            "benchmark_architecture": architecture,
            "gold_label_policy": group_rows[0].get("gold_label_policy", ""),
            "gatekeeper_preset": gatekeeper_preset,
            "gatekeeper_model_label": gatekeeper_model_label,
            "orchestrator_policy": orchestrator_policy,
            "orchestrator_preset": orchestrator_preset,
            "orchestrator_model_label": orchestrator_model_label,
            "n_runs": len(group_rows),
            "n_scored_runs": len(scored_rows),
            "n_completed_runs": sum(1 for row in group_rows if row.get("run_status") == "completed"),
            "n_incomplete_runs": sum(1 for row in group_rows if row.get("run_status") == "incomplete"),
            "n_error_runs": sum(1 for row in group_rows if row.get("run_status") == "error"),
            "n_unique_reviews": len({row.get("review_key", "") for row in group_rows}),
            "parse_success_rate": _mean_for(
                [{"value": 1.0 if row.get("parse_success") else 0.0} for row in group_rows],
                "value",
            ),
            "mean_decision_coverage": _mean_for(group_rows, "decision_coverage"),
            "mean_accuracy": _mean_for(scored_rows, "accuracy"),
            "mean_precision": _mean_for(scored_rows, "precision"),
            "mean_recall": _mean_for(scored_rows, "recall"),
            "mean_specificity": _mean_for(scored_rows, "specificity"),
            "mean_f1": _mean_for(scored_rows, "f1"),
            "mean_duration_seconds": _mean_for(group_rows, "duration_seconds"),
            "mean_duration_per_study_seconds": _mean_for(group_rows, "duration_per_study_seconds"),
            "mean_total_tokens": _mean_for(group_rows, "total_tokens"),
            "mean_total_steps": _mean_for(group_rows, "total_steps"),
            "mean_retry_count": _mean_for(group_rows, "retry_count"),
            "mean_resume_count": _mean_for(group_rows, "resume_count"),
            "mean_rationale_reuse_rate": _mean_for(group_rows, "rationale_reuse_rate"),
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
    for rank, row in enumerate(aggregates, start=1):
        row["rank"] = rank
    return aggregates


def _expected_completion_keys(rows: list[dict]) -> set[tuple[str, int]]:
    expected: set[tuple[str, int]] = set()
    for row in rows:
        review_keys = row.get("_summary_review_keys") or []
        if not review_keys:
            review_key = str(row.get("review_key", ""))
            review_keys = [review_key] if review_key else []
        repeats = _as_int(row.get("_summary_repeats")) or 1
        for review_key in review_keys:
            for run_index in range(1, repeats + 1):
                expected.add((str(review_key), run_index))
    return expected


def _scored_completion_keys(rows: list[dict]) -> set[tuple[str, int]]:
    return {
        (str(row.get("review_key", "")), _as_int(row.get("run_index")) or 1)
        for row in rows
        if row.get("scored_for_aggregate") and str(row.get("review_key", ""))
    }


def _complete_model_group_report(
    rows: list[dict],
) -> tuple[list[dict], list[dict]]:
    grouped: dict[tuple, list[dict]] = defaultdict(list)
    for row in rows:
        grouped[_model_group_key(row)].append(row)

    complete_rows: list[dict] = []
    excluded_groups: list[dict] = []
    for key, group_rows in grouped.items():
        expected_keys = _expected_completion_keys(group_rows)
        scored_keys = _scored_completion_keys(group_rows)
        missing_keys = sorted(expected_keys - scored_keys)
        if not expected_keys or not missing_keys:
            complete_rows.extend(group_rows)
            continue

        (
            architecture,
            gatekeeper_preset,
            orchestrator_policy,
            orchestrator_preset,
            gatekeeper_model_label,
            orchestrator_model_label,
        ) = key
        excluded_groups.append({
            "benchmark_architecture": architecture,
            "gold_label_policy": group_rows[0].get("gold_label_policy", ""),
            "suite": group_rows[0].get("suite", ""),
            "gatekeeper_preset": gatekeeper_preset,
            "gatekeeper_model_label": gatekeeper_model_label,
            "orchestrator_policy": orchestrator_policy,
            "orchestrator_preset": orchestrator_preset,
            "orchestrator_model_label": orchestrator_model_label,
            "n_expected_runs": len(expected_keys),
            "n_scored_runs": len(scored_keys & expected_keys),
            "n_source_rows": len(group_rows),
            "missing_review_keys": sorted({review_key for review_key, _run_index in missing_keys}),
            "source_summary_jsons": sorted({
                row.get("source_summary_json", "")
                for row in group_rows
                if row.get("source_summary_json")
            }),
        })

    return complete_rows, sorted(
        excluded_groups,
        key=lambda row: (
            row.get("suite", ""),
            row.get("gold_label_policy", ""),
            row.get("benchmark_architecture", ""),
            row.get("gatekeeper_preset", ""),
        ),
    )


def _aggregate_review_rows(rows: list[dict]) -> list[dict]:
    grouped: dict[tuple, list[dict]] = defaultdict(list)
    for row in rows:
        grouped[(
            row.get("review_key", ""),
            row.get("review_title", ""),
            row.get("review_url", ""),
            _as_int(row.get("n_studies")),
            _as_int(row.get("gold_pass_count")),
            _as_int(row.get("gold_exclude_count")),
            *_model_group_key(row),
        )].append(row)

    aggregates = []
    for key, group_rows in grouped.items():
        (
            review_key,
            review_title,
            review_url,
            n_studies,
            gold_pass_count,
            gold_exclude_count,
            architecture,
            gatekeeper_preset,
            orchestrator_policy,
            orchestrator_preset,
            gatekeeper_model_label,
            orchestrator_model_label,
        ) = key
        scored_rows = [row for row in group_rows if bool(row.get("scored_for_aggregate"))]
        band = size_band_for(n_studies)
        aggregates.append({
            "benchmark_architecture": architecture,
            "gold_label_policy": group_rows[0].get("gold_label_policy", ""),
            "suite": group_rows[0].get("suite", ""),
            "review_key": review_key,
            "review_title": review_title,
            "review_url": review_url,
            "split": group_rows[0].get("split", ""),
            "n_studies": n_studies,
            "size_band": band["key"],
            "size_band_label": band["label"],
            "gold_pass_count": gold_pass_count,
            "gold_exclude_count": gold_exclude_count,
            "gatekeeper_preset": gatekeeper_preset,
            "gatekeeper_model_label": gatekeeper_model_label,
            "orchestrator_policy": orchestrator_policy,
            "orchestrator_preset": orchestrator_preset,
            "orchestrator_model_label": orchestrator_model_label,
            "n_runs": len(group_rows),
            "n_scored_runs": len(scored_rows),
            "n_completed_runs": sum(1 for row in group_rows if row.get("run_status") == "completed"),
            "n_incomplete_runs": sum(1 for row in group_rows if row.get("run_status") == "incomplete"),
            "n_error_runs": sum(1 for row in group_rows if row.get("run_status") == "error"),
            "parse_success_rate": _mean_for(
                [{"value": 1.0 if row.get("parse_success") else 0.0} for row in group_rows],
                "value",
            ),
            "mean_decision_coverage": _mean_for(group_rows, "decision_coverage"),
            "mean_accuracy": _mean_for(scored_rows, "accuracy"),
            "mean_precision": _mean_for(scored_rows, "precision"),
            "mean_recall": _mean_for(scored_rows, "recall"),
            "mean_specificity": _mean_for(scored_rows, "specificity"),
            "mean_f1": _mean_for(scored_rows, "f1"),
            "mean_duration_seconds": _mean_for(group_rows, "duration_seconds"),
            "mean_total_tokens": _mean_for(group_rows, "total_tokens"),
            "mean_total_steps": _mean_for(group_rows, "total_steps"),
            "mean_rationale_reuse_rate": _mean_for(group_rows, "rationale_reuse_rate"),
        })

    aggregates.sort(
        key=lambda row: (
            row["n_studies"],
            row["review_key"],
            -(row["mean_f1"] or -1.0),
            -(row["mean_recall"] or -1.0),
            -(row["mean_accuracy"] or -1.0),
        )
    )
    return aggregates


def _aggregate_size_bands(rows: list[dict]) -> list[dict]:
    results = []
    for band in SIZE_BANDS:
        band_rows = [
            row
            for row in rows
            if size_band_for(_as_int(row.get("n_studies")))["key"] == band["key"]
        ]
        if not band_rows:
            continue
        results.append({
            "size_band": band["key"],
            "size_band_label": band["label"],
            "leaderboard": _aggregate_model_rows(band_rows),
            "review_rows": _aggregate_review_rows(band_rows),
        })
    return results


def _write_json(path: Path, payload: dict | list) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)


def _write_leaderboard_md(path: Path, title: str, rows: list[dict]) -> None:
    lines = [
        f"# {title}",
        "",
        "| Rank | Architecture | Gatekeeper Model | Runs | Scored | F1 | Recall | Precision | Accuracy | Specificity | Parse Success | Coverage | Mean Tokens | Mean Steps |",
        "|------|--------------|------------------|------|--------|----|--------|-----------|----------|-------------|---------------|----------|-------------|------------|",
    ]
    for rank, row in enumerate(rows, start=1):
        lines.append(
            "| {rank} | {architecture} | {model} | {runs} | {scored} | {f1} | {recall} | {precision} | {accuracy} | {specificity} | {parse_success} | {coverage} | {tokens} | {steps} |".format(
                rank=rank,
                architecture=row.get("benchmark_architecture", ""),
                model=row.get("gatekeeper_model_label", ""),
                runs=row.get("n_runs", 0),
                scored=row.get("n_scored_runs", 0),
                f1=_format_metric(row.get("mean_f1")),
                recall=_format_metric(row.get("mean_recall")),
                precision=_format_metric(row.get("mean_precision")),
                accuracy=_format_metric(row.get("mean_accuracy")),
                specificity=_format_metric(row.get("mean_specificity")),
                parse_success=_format_metric(row.get("parse_success_rate")),
                coverage=_format_metric(row.get("mean_decision_coverage")),
                tokens=_format_metric(row.get("mean_total_tokens")),
                steps=_format_metric(row.get("mean_total_steps")),
            )
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_review_leaderboard_md(path: Path, rows: list[dict]) -> None:
    grouped: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        grouped[row.get("review_key", "")].append(row)

    lines = ["# Totals Review Leaderboard", ""]
    for review_key, review_rows in grouped.items():
        first = review_rows[0]
        sorted_rows = sorted(
            review_rows,
            key=lambda row: (
                row["mean_f1"] is not None,
                row["mean_f1"] or -1.0,
                row["mean_recall"] or -1.0,
                row["mean_accuracy"] or -1.0,
            ),
            reverse=True,
        )
        lines.extend([
            f"## {review_key}",
            "",
            f"**Title:** {first.get('review_title', '')}",
            f"**Studies:** {first.get('n_studies', 0)} | **Size band:** {first.get('size_band_label', '')}",
            "",
            "| Rank | Architecture | Gatekeeper Model | Runs | Scored | F1 | Recall | Precision | Accuracy | Specificity |",
            "|------|--------------|------------------|------|--------|----|--------|-----------|----------|-------------|",
        ])
        for rank, row in enumerate(sorted_rows, start=1):
            lines.append(
                "| {rank} | {architecture} | {model} | {runs} | {scored} | {f1} | {recall} | {precision} | {accuracy} | {specificity} |".format(
                    rank=rank,
                    architecture=row.get("benchmark_architecture", ""),
                    model=row.get("gatekeeper_model_label", ""),
                    runs=row.get("n_runs", 0),
                    scored=row.get("n_scored_runs", 0),
                    f1=_format_metric(row.get("mean_f1")),
                    recall=_format_metric(row.get("mean_recall")),
                    precision=_format_metric(row.get("mean_precision")),
                    accuracy=_format_metric(row.get("mean_accuracy")),
                    specificity=_format_metric(row.get("mean_specificity")),
                )
            )
        lines.append("")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_size_bands_md(path: Path, rows: list[dict]) -> None:
    lines = ["# Horizontal Size-Band Summary", ""]
    for band in rows:
        lines.extend([
            f"## {band['size_band']} ({band['size_band_label']})",
            "",
            "### Model Averages",
            "",
            "| Rank | Architecture | Preset | Gatekeeper Model | Runs | Scored | Reviews | F1 | Recall | Precision | Accuracy |",
            "|------|--------------|--------|------------------|------|--------|---------|----|--------|-----------|----------|",
        ])
        for rank, row in enumerate(band["leaderboard"], start=1):
            lines.append(
                "| {rank} | {architecture} | {preset} | {model} | {runs} | {scored} | {reviews} | {f1} | {recall} | {precision} | {accuracy} |".format(
                    rank=rank,
                    architecture=row.get("benchmark_architecture", ""),
                    preset=row.get("gatekeeper_preset", ""),
                    model=row.get("gatekeeper_model_label", ""),
                    runs=row.get("n_runs", 0),
                    scored=row.get("n_scored_runs", 0),
                    reviews=row.get("n_unique_reviews", 0),
                    f1=_format_metric(row.get("mean_f1")),
                    recall=_format_metric(row.get("mean_recall")),
                    precision=_format_metric(row.get("mean_precision")),
                    accuracy=_format_metric(row.get("mean_accuracy")),
                )
            )
        lines.extend([
            "",
            "### Review Rows",
            "",
            "| Review | Suite | Studies | Architecture | Preset | Gatekeeper Model | Runs | Scored | F1 | Recall | Precision | Accuracy |",
            "|--------|-------|---------|--------------|--------|------------------|------|--------|----|--------|-----------|----------|",
        ])
        for row in band.get("review_rows", []):
            lines.append(
                "| {review} | {suite} | {studies} | {architecture} | {preset} | {model} | {runs} | {scored} | {f1} | {recall} | {precision} | {accuracy} |".format(
                    review=row.get("review_key", ""),
                    suite=row.get("suite", ""),
                    studies=row.get("n_studies", 0),
                    architecture=row.get("benchmark_architecture", ""),
                    preset=row.get("gatekeeper_preset", ""),
                    model=row.get("gatekeeper_model_label", ""),
                    runs=row.get("n_runs", 0),
                    scored=row.get("n_scored_runs", 0),
                    f1=_format_metric(row.get("mean_f1")),
                    recall=_format_metric(row.get("mean_recall")),
                    precision=_format_metric(row.get("mean_precision")),
                    accuracy=_format_metric(row.get("mean_accuracy")),
                )
            )
        lines.append("")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_per_sr_leaderboards(root: Path, review_rows: list[dict]) -> None:
    grouped: dict[str, list[dict]] = defaultdict(list)
    for row in review_rows:
        grouped[row.get("review_key", "")].append(row)

    per_sr_dir = root / "per_sr"
    per_sr_dir.mkdir(parents=True, exist_ok=True)
    for review_key, rows in grouped.items():
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
        payload = {
            "generated_at": datetime.now().isoformat(),
            "review_key": review_key,
            "review_title": rows[0].get("review_title", ""),
            "n_studies": rows[0].get("n_studies", 0),
            "size_band": rows[0].get("size_band", ""),
            "size_band_label": rows[0].get("size_band_label", ""),
            "leaderboard": sorted_rows,
        }
        _write_json(per_sr_dir / f"{review_key}_leaderboard.json", payload)
        _write_review_leaderboard_md(per_sr_dir / f"{review_key}_leaderboard.md", sorted_rows)


def _remove_legacy_suite_horizontal_files(target_dir: Path) -> None:
    for filename in ("horizontal_size_bands.json", "horizontal_size_bands.md"):
        path = target_dir / filename
        if path.exists():
            path.unlink()


def _write_horizontal_comparison_groups(
    *,
    totals_root: Path,
    grouped_rows: dict[tuple[str, str, str], list[dict]],
) -> list[dict]:
    horizontal_groups = []
    by_policy_architecture: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for (_suite, label_policy, architecture), rows in grouped_rows.items():
        by_policy_architecture[(label_policy, architecture)].extend(rows)

    for (label_policy, architecture), rows in sorted(by_policy_architecture.items()):
        if not label_policy or not architecture:
            continue
        rows = _dedupe_latest_model_review_runs(rows, separate_suites=False)
        target_dir = totals_root / "horizontal_comparison" / _policy_dir_name(label_policy) / architecture
        target_dir.mkdir(parents=True, exist_ok=True)
        size_bands = _aggregate_size_bands(rows)
        metadata = {
            "generated_at": datetime.now().isoformat(),
            "gold_label_policy": label_policy,
            "benchmark_architecture": architecture,
            "n_source_runs": len(rows),
            "source_summary_count": len({row.get("source_summary_json", "") for row in rows}),
            "source_suites": sorted({row.get("suite", "") for row in rows if row.get("suite")}),
            "deduplication": (
                "one row per policy/review/architecture/model variant across suites; "
                "provider ignored; repeat=1 summaries preferred, then newest source"
            ),
        }
        _write_json(
            target_dir / "horizontal_size_bands.json",
            {**metadata, "size_bands": size_bands},
        )
        _write_size_bands_md(
            target_dir / "horizontal_size_bands.md",
            size_bands,
        )
        horizontal_groups.append({
            **metadata,
            "directory": _repo_relative_path(target_dir),
        })
    return horizontal_groups


def write_screening_totals(
    *,
    output_root: Path | None = None,
    totals_root: Path | None = None,
    source_mode: str = "discover",
    canonical_gold_label_policies: Iterable[str] | None = DEFAULT_CANONICAL_GOLD_LABEL_POLICIES,
) -> dict:
    """
    Write aggregate totals across screening benchmark policy summaries.

    Aggregation is separated by suite, gold-label policy, and benchmark
    architecture.  Older summaries without an architecture field are treated as
    ``batch_orchestrator_v1``.
    """
    if source_mode not in SOURCE_MODES:
        raise ValueError(f"source_mode must be one of {SOURCE_MODES}: {source_mode}")
    output_root = output_root or (OUTPUT_DIR / "screening_benchmarks")
    totals_root = totals_root or (output_root / "totals")
    if source_mode == "canonical":
        all_runs = _load_runs_from_canonical_sources(totals_root=totals_root)
        policy_set = set(canonical_gold_label_policies or [])
        if policy_set:
            all_runs = [
                row
                for row in all_runs
                if row.get("gold_label_policy", "") in policy_set
            ]
    else:
        all_runs: list[dict] = []
        for summary_path in _summary_paths(output_root):
            all_runs.extend(_load_policy_runs(summary_path))
    raw_source_run_count = len(all_runs)
    if source_mode == "discover":
        all_runs = [row for row in all_runs if not _is_repetition_source(row)]
        all_runs = _dedupe_latest_model_review_runs(all_runs)

    grouped: dict[tuple[str, str, str], list[dict]] = defaultdict(list)
    for row in all_runs:
        grouped[(
            row.get("suite", ""),
            row.get("gold_label_policy", ""),
            row.get("benchmark_architecture", BATCH_ARCHITECTURE),
        )].append(row)

    written_groups = []
    complete_grouped: dict[tuple[str, str, str], list[dict]] = {}
    for (suite, label_policy, architecture), rows in grouped.items():
        if not suite or not label_policy:
            continue
        target_dir = totals_root / suite / _policy_dir_name(label_policy) / architecture
        target_dir.mkdir(parents=True, exist_ok=True)
        complete_rows, excluded_incomplete_model_groups = _complete_model_group_report(rows)
        complete_grouped[(suite, label_policy, architecture)] = complete_rows
        leaderboard = _aggregate_model_rows(complete_rows)
        review_leaderboard = _aggregate_review_rows(complete_rows)
        metadata = {
            "generated_at": datetime.now().isoformat(),
            "suite": suite,
            "gold_label_policy": label_policy,
            "benchmark_architecture": architecture,
            "n_source_runs": len(rows),
            "n_aggregated_source_runs": len(complete_rows),
            "n_excluded_incomplete_model_groups": len(excluded_incomplete_model_groups),
            "n_raw_source_runs": raw_source_run_count,
            "source_summary_count": len({row.get("source_summary_json", "") for row in rows}),
            "source_mode": source_mode,
            "canonical_gold_label_policies": (
                list(canonical_gold_label_policies or [])
                if source_mode == "canonical"
                else []
            ),
            "deduplication": (
                "canonical manifest entries only"
                if source_mode == "canonical"
                else (
                    "none; every discovered run is included"
                    if source_mode == "all"
                    else (
                        "one row per suite/policy/review/architecture/model variant; "
                        "provider ignored; _repN folders ignored; "
                        "repeat=1 summaries preferred, then newest source"
                    )
                )
            ),
        }

        _write_json(
            target_dir / "totals_leaderboard.json",
            {
                **metadata,
                "leaderboard": leaderboard,
                "excluded_incomplete_model_groups": excluded_incomplete_model_groups,
            },
        )
        _write_json(
            target_dir / "totals_review_leaderboard.json",
            {
                **metadata,
                "review_leaderboard": review_leaderboard,
                "excluded_incomplete_model_groups": excluded_incomplete_model_groups,
            },
        )
        _write_leaderboard_md(
            target_dir / "totals_leaderboard.md",
            "Totals Leaderboard",
            leaderboard,
        )
        _write_review_leaderboard_md(
            target_dir / "totals_review_leaderboard.md",
            review_leaderboard,
        )
        _remove_legacy_suite_horizontal_files(target_dir)
        _write_per_sr_leaderboards(target_dir, review_leaderboard)
        written_groups.append({
            **metadata,
            "directory": _repo_relative_path(target_dir),
        })

    horizontal_groups = _write_horizontal_comparison_groups(
        totals_root=totals_root,
        grouped_rows=complete_grouped,
    )
    _write_json(
        totals_root / "totals_index.json",
        {
            "generated_at": datetime.now().isoformat(),
            "totals_root": _repo_relative_path(totals_root),
            "source_mode": source_mode,
            "groups": written_groups,
            "horizontal_comparison_groups": horizontal_groups,
        },
    )
    return {
        "totals_root": _repo_relative_path(totals_root),
        "source_mode": source_mode,
        "groups": written_groups,
        "horizontal_comparison_groups": horizontal_groups,
    }
