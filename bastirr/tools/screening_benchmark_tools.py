"""
Tools used by the screening benchmark harness.

These helpers persist and format Gatekeeper-only outputs without relying on
the full end-to-end report/evidence path that expects Miner and Critic data.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

from smolagents import tool

from bastirr.tools.report_tools import _parse_decisions


def _evidence_path(output_dir: str | os.PathLike[str]) -> Path:
    return Path(output_dir) / "evidence.json"


def _progress_path(output_dir: str | os.PathLike[str]) -> Path:
    return Path(output_dir) / "screening_progress.json"


def _read_existing_decisions(output_dir: str | os.PathLike[str]) -> list[dict]:
    path = _evidence_path(output_dir)
    if not path.exists():
        return []
    with open(path, "r", encoding="utf-8") as f:
        payload = json.load(f)
    decisions = payload.get("screening_decisions", [])
    return decisions if isinstance(decisions, list) else []


def _normalize_screening_decision(decision: dict) -> dict:
    return {
        "study_index": int(decision.get("study_index", 0)),
        "title": str(decision.get("title", "") or ""),
        "decision": str(decision.get("decision", "") or "").upper(),
        "reason": str(
            decision.get("reason", decision.get("rationale", "")) or ""
        ).strip(),
        "confidence": str(decision.get("confidence", "") or "").strip(),
    }


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


def _write_screening_artifacts(
    output_dir: str | os.PathLike[str],
    decisions: list[dict],
    *,
    expected_n_studies: int | None = None,
) -> None:
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    ordered = sorted(
        (_normalize_screening_decision(decision) for decision in decisions),
        key=lambda item: item["study_index"],
    )
    with open(_evidence_path(output_dir), "w", encoding="utf-8") as f:
        json.dump({"screening_decisions": ordered}, f, ensure_ascii=False, indent=2)

    progress = {
        "expected_n_studies": expected_n_studies,
        "completed_count": len(ordered),
        "completed_study_indices": [decision["study_index"] for decision in ordered],
        "next_study_index": _next_missing_index(ordered, expected_n_studies),
        "screening_decisions": ordered,
    }
    with open(_progress_path(output_dir), "w", encoding="utf-8") as f:
        json.dump(progress, f, ensure_ascii=False, indent=2)


@tool
def save_screening_evidence_json(
    screening_response: str,
    output_dir: str,
    expected_n_studies: int | None = None,
) -> str:
    """
    Save screening-only outputs in a screening-specific evidence.json shape.

    Args:
        screening_response: Raw response string from the Gatekeeper.
        output_dir: Directory where ``evidence.json`` should be written.
        expected_n_studies: Optional expected number of unique study decisions.
            When provided, the tool fails closed if the parsed decision count
            does not exactly match this value.

    Returns:
        A status string describing the saved file path.
    """
    decisions = _parse_decisions(screening_response)
    if expected_n_studies is not None and len(decisions) != expected_n_studies:
        raise ValueError(
            "Incomplete screening response: expected "
            f"{expected_n_studies} parsed decisions, found {len(decisions)}. "
            "Do not save partial or grouped screening outputs."
        )

    _write_screening_artifacts(
        output_dir,
        decisions,
        expected_n_studies=expected_n_studies,
    )
    output_path = os.path.join(output_dir, "evidence.json")
    return f"Screening evidence saved to {output_path}"


@tool
def append_screening_decision_json(
    screening_response: str,
    output_dir: str,
    expected_study_index: int,
    expected_n_studies: int | None = None,
) -> str:
    """
    Append one Gatekeeper screening decision to loop benchmark artifacts.

    Args:
        screening_response: Raw response string from the single-study Gatekeeper.
        output_dir: Directory where ``evidence.json`` and
            ``screening_progress.json`` should be updated.
        expected_study_index: One-based study index that must appear in the
            parsed Gatekeeper response.
        expected_n_studies: Optional total number of studies in the review.

    Returns:
        A concise status string with completion progress.
    """
    decisions = _parse_decisions(screening_response)
    if len(decisions) != 1:
        raise ValueError(
            "Expected exactly one parsed screening decision, found "
            f"{len(decisions)}."
        )

    decision = _normalize_screening_decision(decisions[0])
    expected_index = int(expected_study_index)
    if decision["study_index"] != expected_index:
        raise ValueError(
            f"Gatekeeper returned study_index {decision['study_index']}, "
            f"expected {expected_index}."
        )
    if decision["decision"] not in {"INCLUDE", "EXCLUDE"}:
        raise ValueError(
            "Gatekeeper decision must be INCLUDE or EXCLUDE, found "
            f"{decision['decision']!r}."
        )

    existing = _read_existing_decisions(output_dir)
    existing_by_index = {
        int(item.get("study_index", 0)): item
        for item in existing
        if str(item.get("study_index", "")).isdigit()
    }
    if expected_index in existing_by_index:
        raise ValueError(f"Study {expected_index} already has a saved decision.")

    updated = list(existing_by_index.values()) + [decision]
    _write_screening_artifacts(
        output_dir,
        updated,
        expected_n_studies=expected_n_studies,
    )
    total = expected_n_studies or len(updated)
    return (
        f"Saved decision for study {expected_index}. "
        f"Progress: {len(updated)}/{total}."
    )


@tool
def append_screening_chunk_decisions_json(
    screening_response: str,
    output_dir: str,
    expected_study_indices_json: str,
    expected_n_studies: int | None = None,
) -> str:
    """
    Append one mini-batch Gatekeeper screening chunk to benchmark artifacts.

    Args:
        screening_response: Raw response string from the chunk Gatekeeper.
        output_dir: Directory where ``evidence.json`` and
            ``screening_progress.json`` should be updated.
        expected_study_indices_json: JSON array of one-based study indices
            that must appear exactly once in the parsed Gatekeeper response.
        expected_n_studies: Optional total number of studies in the review.

    Returns:
        A concise status string with completion progress.
    """
    try:
        expected_indices = [int(index) for index in json.loads(expected_study_indices_json)]
    except (TypeError, ValueError, json.JSONDecodeError) as exc:
        raise ValueError(
            "expected_study_indices_json must be a JSON array of study indices."
        ) from exc
    if not expected_indices:
        raise ValueError("expected_study_indices_json must not be empty.")
    if len(expected_indices) != len(set(expected_indices)):
        raise ValueError("expected_study_indices_json contains duplicate indices.")

    decisions = [_normalize_screening_decision(decision) for decision in _parse_decisions(screening_response)]
    decision_by_index: dict[int, dict] = {}
    invalid_decisions: list[str] = []
    for decision in decisions:
        index = decision["study_index"]
        if index in decision_by_index:
            raise ValueError(f"Gatekeeper returned duplicate decision for study {index}.")
        if decision["decision"] not in {"INCLUDE", "EXCLUDE"}:
            invalid_decisions.append(f"{index}: {decision['decision']!r}")
        decision_by_index[index] = decision
    if invalid_decisions:
        raise ValueError(
            "Gatekeeper decisions must be INCLUDE or EXCLUDE; invalid values: "
            + ", ".join(invalid_decisions)
        )

    expected_set = set(expected_indices)
    returned_set = set(decision_by_index)
    if returned_set != expected_set:
        missing = sorted(expected_set - returned_set)
        extra = sorted(returned_set - expected_set)
        raise ValueError(
            "Chunk response did not match expected study indices "
            f"(missing={missing}, extra={extra})."
        )

    existing = _read_existing_decisions(output_dir)
    existing_by_index = {
        int(item.get("study_index", 0)): item
        for item in existing
        if str(item.get("study_index", "")).isdigit()
    }
    already_saved = sorted(expected_set.intersection(existing_by_index))
    if already_saved:
        raise ValueError(
            "Study decisions already saved for chunk index/indices: "
            + ", ".join(str(index) for index in already_saved)
        )

    updated = list(existing_by_index.values()) + [
        decision_by_index[index]
        for index in expected_indices
    ]
    _write_screening_artifacts(
        output_dir,
        updated,
        expected_n_studies=expected_n_studies,
    )
    total = expected_n_studies or len(updated)
    return (
        f"Saved chunk decisions for studies {expected_indices[0]}..{expected_indices[-1]} "
        f"({len(expected_indices)} decisions). Progress: {len(updated)}/{total}."
    )


@tool
def format_screening_progress_summary(
    review_title: str,
    output_dir: str,
) -> str:
    """
    Build a short human-readable summary from the saved loop evidence file.

    Args:
        review_title: Review title used in the summary heading.
        output_dir: Directory containing ``evidence.json``.

    Returns:
        A short Markdown summary of the saved screening decisions.
    """
    decisions = _read_existing_decisions(output_dir)
    included = sum(
        1 for decision in decisions if str(decision.get("decision", "")).upper() == "INCLUDE"
    )
    excluded = sum(
        1 for decision in decisions if str(decision.get("decision", "")).upper() == "EXCLUDE"
    )
    return (
        f"# Screening Summary\n\n"
        f"- **Review:** {review_title}\n"
        f"- **Total decisions saved:** {len(decisions)}\n"
        f"- **Included:** {included}\n"
        f"- **Excluded:** {excluded}\n"
    )


@tool
def format_screening_summary(
    review_title: str,
    screening_response: str,
) -> str:
    """
    Build a short human-readable screening summary from Gatekeeper output.

    Args:
        review_title: Review title used in the summary heading.
        screening_response: Raw response string from the Gatekeeper.

    Returns:
        A short Markdown summary of the screening run.
    """
    decisions = _parse_decisions(screening_response)
    included = sum(
        1 for decision in decisions if decision.get("decision", "").upper() == "INCLUDE"
    )
    excluded = sum(
        1 for decision in decisions if decision.get("decision", "").upper() == "EXCLUDE"
    )

    if not decisions:
        return (
            f"# Screening Summary\n\n"
            f"- **Review:** {review_title}\n"
            f"- **Status:** No screening decisions could be parsed.\n"
        )

    return (
        f"# Screening Summary\n\n"
        f"- **Review:** {review_title}\n"
        f"- **Total decisions parsed:** {len(decisions)}\n"
        f"- **Included:** {included}\n"
        f"- **Excluded:** {excluded}\n"
    )
