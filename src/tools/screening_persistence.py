"""
Screening decision persistence (evidence.json + screening_progress.json).

Used by Orchestrator screening helpers (``append_screening_batch``) and by
analysis tools that read saved decisions. Writes a screening-specific
``evidence.json`` shape (decisions only).
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from smolagents import tool

_VALID_FINAL_DECISIONS = {"INCLUDE", "EXCLUDE", "UNCLEAR"}


def evidence_path(output_dir: str | os.PathLike[str]) -> Path:
    return Path(output_dir) / "evidence.json"


def progress_path(output_dir: str | os.PathLike[str]) -> Path:
    return Path(output_dir) / "screening_progress.json"


def read_existing_decisions(output_dir: str | os.PathLike[str]) -> list[dict]:
    path = evidence_path(output_dir)
    if not path.exists():
        return []
    with open(path, "r", encoding="utf-8") as f:
        payload = json.load(f)
    decisions = payload.get("screening_decisions", [])
    return decisions if isinstance(decisions, list) else []


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

    Accepts the criteria-based schema (``final_decision`` + ``criteria``) and
    legacy records that used ``decision`` / ``rationale`` / ``confidence``.
    """
    final = str(
        decision.get("final_decision", decision.get("decision", "")) or ""
    ).upper()
    return {
        "study_index": int(decision.get("study_index", 0)),
        "final_decision": final,
        # Alias kept for downstream miner / report tools that still read
        # ``decision`` on persisted records.
        "decision": final,
        "criteria": _normalize_criteria(decision.get("criteria")),
        "title": str(decision.get("title", "") or ""),
    }


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
    decisions = payload.get("decisions")
    if not isinstance(decisions, list):
        raise ValueError(
            "Gatekeeper screening response must contain a decisions list."
        )
    return [item for item in decisions if isinstance(item, dict)]


def _next_missing_index(decisions: list[dict], expected_n_studies: int | None) -> int | None:
    if expected_n_studies is None:
        return None
    completed = {
        int(decision.get("study_index", 0))
        for decision in decisions
        if str(decision.get("study_index", "")).isdigit()
    }
    for index in range(1, expected_n_studies + 1):
        if index not in completed:
            return index
    return None


def write_screening_artifacts(
    output_dir: str | os.PathLike[str],
    decisions: list[dict],
    *,
    expected_n_studies: int | None = None,
) -> None:
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    ordered = sorted(
        (normalize_screening_decision(decision) for decision in decisions),
        key=lambda item: item["study_index"],
    )
    with open(evidence_path(output_dir), "w", encoding="utf-8") as f:
        json.dump({"screening_decisions": ordered}, f, ensure_ascii=False, indent=2)

    progress = {
        "expected_n_studies": expected_n_studies,
        "completed_count": len(ordered),
        "completed_study_indices": [decision["study_index"] for decision in ordered],
        "next_study_index": _next_missing_index(ordered, expected_n_studies),
        "screening_decisions": ordered,
    }
    with open(progress_path(output_dir), "w", encoding="utf-8") as f:
        json.dump(progress, f, ensure_ascii=False, indent=2)

    if expected_n_studies is not None and len(ordered) == int(expected_n_studies):
        # Local import avoids a cycle with mentor.tools.validation.screening_artifacts.
        from mentor.tools.validation import validate_screening_artifacts_consistent

        validate_screening_artifacts_consistent(
            output_dir,
            expected_n_studies=int(expected_n_studies),
        )


def append_batch_decisions(
    screening_response: str,
    output_dir: str | os.PathLike[str],
    expected_indices: list[int],
    *,
    expected_n_studies: int | None = None,
) -> list[dict]:
    """
    Validate a Gatekeeper response for ``expected_indices`` and append to artifacts.

    Returns the updated full decision list. Raises ``ValueError`` on mismatch
    (fail closed; no fallback decisions).
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
        if decision["final_decision"] not in _VALID_FINAL_DECISIONS:
            invalid_decisions.append(f"{index}: {decision['final_decision']!r}")
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
    write_screening_artifacts(
        output_dir,
        updated,
        expected_n_studies=expected_n_studies,
    )
    return updated


def decisions_to_screening_response(decisions: list[dict]) -> str:
    """Serialize decisions into a Gatekeeper-shaped JSON string for downstream tools."""
    ordered = sorted(
        (normalize_screening_decision(d) for d in decisions),
        key=lambda item: item["study_index"],
    )
    included = sum(1 for d in ordered if d["final_decision"] == "INCLUDE")
    excluded = sum(1 for d in ordered if d["final_decision"] == "EXCLUDE")
    unclear = sum(1 for d in ordered if d["final_decision"] == "UNCLEAR")
    payload_decisions = [
        {
            "study_index": d["study_index"],
            "criteria": d["criteria"],
            "final_decision": d["final_decision"],
        }
        for d in ordered
    ]
    return json.dumps(
        {
            "n_total": len(ordered),
            "n_included": included,
            "n_excluded": excluded,
            "n_unclear": unclear,
            "decisions": payload_decisions,
        },
        ensure_ascii=False,
    )


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
    decisions = read_existing_decisions(output_dir)
    included = sum(
        1
        for decision in decisions
        if str(decision.get("final_decision", decision.get("decision", ""))).upper()
        == "INCLUDE"
    )
    excluded = sum(
        1
        for decision in decisions
        if str(decision.get("final_decision", decision.get("decision", ""))).upper()
        == "EXCLUDE"
    )
    unclear = sum(
        1
        for decision in decisions
        if str(decision.get("final_decision", decision.get("decision", ""))).upper()
        == "UNCLEAR"
    )
    return (
        f"# Screening Summary\n\n"
        f"- **Review:** {review_title}\n"
        f"- **Total decisions saved:** {len(decisions)}\n"
        f"- **Included:** {included}\n"
        f"- **Excluded:** {excluded}\n"
        f"- **Unclear:** {unclear}\n"
    )
