"""Validate evidence.json and screening_progress.json after persistence."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from mentor.tools.screening_persistence import (
    evidence_path,
    normalize_screening_decision,
    progress_path,
    _next_missing_index,
)


def _decisions_by_index(
    decisions: Any,
    *,
    source: str,
    expected_n_studies: int,
) -> dict[int, dict]:
    if not isinstance(decisions, list):
        raise ValueError(f"Invalid {source}: screening decisions must be a list.")
    by_index: dict[int, dict] = {}
    for position, raw in enumerate(decisions, start=1):
        if not isinstance(raw, dict):
            raise ValueError(
                f"Invalid {source}: decision at position {position} is not an object."
            )
        decision = normalize_screening_decision(raw)
        index = decision["study_index"]
        if index < 1 or index > expected_n_studies:
            raise ValueError(
                f"Invalid {source}: study_index {index} outside 1..{expected_n_studies}."
            )
        if index in by_index:
            raise ValueError(f"Invalid {source}: duplicate decision for study {index}.")
        final = str(
            decision.get("final_decision", decision.get("decision", ""))
        ).upper()
        if final not in {"INCLUDE", "EXCLUDE", "UNCLEAR"}:
            raise ValueError(
                f"Invalid {source}: study {index} has decision "
                f"{final!r}; expected INCLUDE, EXCLUDE, or UNCLEAR."
            )
        by_index[index] = decision
    return by_index


def validate_screening_artifacts_consistent(
    output_dir: str | os.PathLike[str],
    *,
    expected_n_studies: int,
) -> None:
    """Fail closed if evidence.json and screening_progress.json disagree."""
    output_dir = Path(output_dir)
    evidence_file = evidence_path(output_dir)
    progress_file = progress_path(output_dir)
    errors: list[str] = []
    if not evidence_file.is_file():
        errors.append("The expected evidence.json file was not written.")
    if not progress_file.is_file():
        errors.append("The expected screening_progress.json file was not written.")
    if errors:
        raise ValueError(
            "Screening persistence validation failed:\n- " + "\n- ".join(errors)
        )

    try:
        with open(evidence_file, "r", encoding="utf-8") as f:
            evidence_payload = json.load(f)
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"Unable to read valid evidence.json: {exc}") from exc
    try:
        with open(progress_file, "r", encoding="utf-8") as f:
            progress_payload = json.load(f)
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"Unable to read valid screening_progress.json: {exc}") from exc

    if not isinstance(evidence_payload, dict):
        raise ValueError(
            "Screening persistence validation failed:\n- "
            "evidence.json root must be an object."
        )
    if not isinstance(progress_payload, dict):
        raise ValueError(
            "Screening persistence validation failed:\n- "
            "screening_progress.json root must be an object."
        )

    try:
        evidence_by_index = _decisions_by_index(
            evidence_payload.get("screening_decisions"),
            source="evidence.json",
            expected_n_studies=expected_n_studies,
        )
    except ValueError as exc:
        raise ValueError(f"Screening persistence validation failed:\n- {exc}") from exc

    if progress_payload.get("expected_n_studies") != expected_n_studies:
        errors.append(
            "screening_progress.json has an incorrect expected_n_studies value."
        )
    if progress_payload.get("completed_count") != len(evidence_by_index):
        errors.append(
            "screening_progress.json completed_count does not match evidence.json."
        )
    if progress_payload.get("completed_study_indices") != sorted(evidence_by_index):
        errors.append(
            "screening_progress.json completed indices do not match evidence.json."
        )
    expected_next = _next_missing_index(
        list(evidence_by_index.values()),
        expected_n_studies,
    )
    if progress_payload.get("next_study_index") != expected_next:
        errors.append(
            "screening_progress.json next_study_index does not match evidence.json."
        )

    try:
        progress_by_index = _decisions_by_index(
            progress_payload.get("screening_decisions"),
            source="screening_progress.json",
            expected_n_studies=expected_n_studies,
        )
    except ValueError as exc:
        errors.append(str(exc))
        progress_by_index = {}
    if progress_by_index != evidence_by_index:
        errors.append(
            "screening_progress.json decisions do not match evidence.json."
        )

    if errors:
        raise ValueError(
            "Screening persistence validation failed:\n- " + "\n- ".join(errors)
        )
