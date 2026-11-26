"""
Screening decision persistence (``evidence.json``).

Used by Orchestrator screening helpers (``append_screening_batch``) and by
analysis tools that read saved decisions. ``evidence.json`` mirrors the
Gatekeeper answer shape (counts + ``study_decisions``), accumulated across
batches.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from smolagents import tool

_VALID_DECISIONS = {"INCLUDE", "EXCLUDE", "UNCLEAR"}


def evidence_path(output_dir: str | os.PathLike[str]) -> Path:
    return Path(output_dir) / "evidence.json"


def _extract_decisions_list(payload: Any) -> list:
    """Read the study_decisions list; accept legacy list keys."""
    if not isinstance(payload, dict):
        return []
    decisions = payload.get(
        "study_decisions",
        payload.get("decisions", payload.get("screening_decisions", [])),
    )
    return decisions if isinstance(decisions, list) else []


def read_existing_decisions(output_dir: str | os.PathLike[str]) -> list[dict]:
    path = evidence_path(output_dir)
    if not path.exists():
        return []
    with open(path, "r", encoding="utf-8") as f:
        payload = json.load(f)
    return _extract_decisions_list(payload)


def _normalize_criteria(raw_criteria: Any) -> list[dict]:
    if not isinstance(raw_criteria, list):
        return []
    normalized: list[dict] = []
    for item in raw_criteria:
        if not isinstance(item, dict):
            continue
        normalized.append(
            {
                "id": str(item.get("id", "") or ""),
                "label": str(item.get("label", "") or "").upper(),
                "rationale": str(item.get("rationale", "") or "").strip(),
            }
        )
    return normalized


def normalize_screening_decision(decision: dict) -> dict:
    """Normalize a Gatekeeper decision for persistence.

    Canonical verdict key is ``decision``. Legacy ``final_decision`` is
    accepted as a read fallback only.
    """
    verdict = str(
        decision.get("decision", decision.get("final_decision", "")) or ""
    ).upper()
    return {
        "study_index": int(decision.get("study_index", 0)),
        "decision": verdict,
        "criteria": _normalize_criteria(decision.get("criteria")),
    }


def _decision_counts(ordered: list[dict]) -> dict[str, int]:
    included = sum(1 for d in ordered if d["decision"] == "INCLUDE")
    excluded = sum(1 for d in ordered if d["decision"] == "EXCLUDE")
    unclear = sum(1 for d in ordered if d["decision"] == "UNCLEAR")
    return {
        "n_total": len(ordered),
        "n_included": included,
        "n_excluded": excluded,
        "n_unclear": unclear,
    }


def _evidence_payload(ordered: list[dict]) -> dict[str, Any]:
    return {**_decision_counts(ordered), "study_decisions": ordered}


def _parse_screening_response_decisions(screening_response: str) -> list[dict]:
    """Parse Gatekeeper JSON into decision objects (fail closed on bad JSON)."""
    try:
        payload = json.loads(screening_response)
    except json.JSONDecodeError as exc:
        raise ValueError(
            "Gatekeeper screening response is not valid JSON."
        ) from exc
    if not isinstance(payload, dict):
        raise ValueError("Gatekeeper screening response JSON root must be an object.")
    decisions = payload.get("study_decisions", payload.get("decisions"))
    if not isinstance(decisions, list):
        raise ValueError(
            "Gatekeeper screening response must contain a study_decisions list."
        )
    return [item for item in decisions if isinstance(item, dict)]


def write_screening_artifacts(
    output_dir: str | os.PathLike[str],
    decisions: list[dict],
) -> None:
    """Write ``evidence.json`` for the current decision list (no completeness check)."""
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    ordered = sorted(
        (normalize_screening_decision(decision) for decision in decisions),
        key=lambda item: item["study_index"],
    )
    evidence = _evidence_payload(ordered)
    with open(evidence_path(output_dir), "w", encoding="utf-8") as f:
        json.dump(evidence, f, ensure_ascii=False, indent=2)


def append_batch_decisions(
    screening_response: str,
    output_dir: str | os.PathLike[str],
    expected_indices: list[int],
) -> list[dict]:
    """
    Validate a Gatekeeper response for ``expected_indices`` and append to artifacts.

    Returns the updated full decision list. Raises ``ValueError`` on mismatch
    (fail closed; no fallback decisions). Full-run completeness is checked
    separately via ``validate_screening_artifacts``.
    """
    if not expected_indices:
        raise ValueError("expected_indices must not be empty.")
    if len(expected_indices) != len(set(expected_indices)):
        raise ValueError("expected_indices contains duplicate indices.")

    decisions = [
        normalize_screening_decision(decision)
        for decision in _parse_screening_response_decisions(screening_response)
    ]
    decision_by_index: dict[int, dict] = {}
    invalid_decisions: list[str] = []
    for decision in decisions:
        index = decision["study_index"]
        if index in decision_by_index:
            raise ValueError(f"Gatekeeper returned duplicate decision for study {index}.")
        if decision["decision"] not in _VALID_DECISIONS:
            invalid_decisions.append(f"{index}: {decision['decision']!r}")
        decision_by_index[index] = decision
    if invalid_decisions:
        raise ValueError(
            "Gatekeeper decisions must be INCLUDE, EXCLUDE, or UNCLEAR; "
            "invalid values: " + ", ".join(invalid_decisions)
        )

    expected_set = set(expected_indices)
    returned_set = set(decision_by_index)
    if returned_set != expected_set:
        missing = sorted(expected_set - returned_set)
        extra = sorted(returned_set - expected_set)
        raise ValueError(
            "Batch response did not match expected study indices "
            f"(missing={missing}, extra={extra})."
        )

    existing = read_existing_decisions(output_dir)
    existing_by_index = {
        int(item.get("study_index", 0)): item
        for item in existing
        if str(item.get("study_index", "")).isdigit()
    }
    already_saved = sorted(expected_set.intersection(existing_by_index))
    if already_saved:
        raise ValueError(
            "Study decisions already saved for batch index/indices: "
            + ", ".join(str(index) for index in already_saved)
        )

    updated = list(existing_by_index.values()) + [
        decision_by_index[index] for index in expected_indices
    ]
    write_screening_artifacts(output_dir, updated)
    return updated


def decisions_to_screening_response(decisions: list[dict]) -> str:
    """Serialize decisions into a Gatekeeper-shaped JSON string for downstream tools."""
    ordered = sorted(
        (normalize_screening_decision(d) for d in decisions),
        key=lambda item: item["study_index"],
    )
    return json.dumps(_evidence_payload(ordered), ensure_ascii=False)


def batch_indices(indices: list[int], *, batch_size: int | None) -> list[list[int]]:
    """Split ``indices`` into contiguous batches of ``batch_size`` (or one batch)."""
    if not indices:
        return []
    if batch_size is None:
        return [list(indices)]
    if batch_size < 1:
        raise ValueError("batch_size must be at least 1")
    return [
        indices[offset : offset + batch_size]
        for offset in range(0, len(indices), batch_size)
    ]


@tool
def format_screening_progress_summary(
    review_title: str,
    output_dir: str,
) -> str:
    """
    Build a short human-readable summary from the saved screening evidence file.

    Args:
        review_title: Review title used in the summary heading.
        output_dir: Directory containing ``evidence.json``.

    Returns:
        A short Markdown summary of the saved screening decisions.
    """
    decisions = [
        normalize_screening_decision(item)
        for item in read_existing_decisions(output_dir)
        if isinstance(item, dict)
    ]
    counts = _decision_counts(decisions)
    return (
        f"# Screening Summary\n\n"
        f"- **Review:** {review_title}\n"
        f"- **Total decisions saved:** {counts['n_total']}\n"
        f"- **Included:** {counts['n_included']}\n"
        f"- **Excluded:** {counts['n_excluded']}\n"
        f"- **Unclear:** {counts['n_unclear']}\n"
    )
