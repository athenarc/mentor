"""Validate evidence.json after screening persistence."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from mentor.tools.screening_persistence import (
    _decision_counts,
    _extract_decisions_list,
    evidence_path,
    normalize_screening_decision,
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
        verdict = str(decision.get("decision", "")).upper()
        if verdict not in {"INCLUDE", "EXCLUDE", "UNCLEAR"}:
            raise ValueError(
                f"Invalid {source}: study {index} has decision "
                f"{verdict!r}; expected INCLUDE, EXCLUDE, or UNCLEAR."
            )
        by_index[index] = decision
    return by_index


def _validate_counts(payload: dict, ordered: list[dict], *, source: str) -> list[str]:
    expected = _decision_counts(ordered)
    errors: list[str] = []
    for key, value in expected.items():
        if payload.get(key) != value:
            errors.append(
                f"{source} {key} is {payload.get(key)!r}; expected {value}."
            )
    return errors


def validate_screening_artifacts_consistent(
    output_dir: str | os.PathLike[str],
    *,
    expected_n_studies: int,
) -> None:
    """Fail closed if evidence.json is missing, incomplete, or internally inconsistent."""
    output_dir = Path(output_dir)
    evidence_file = evidence_path(output_dir)
    if not evidence_file.is_file():
        raise ValueError(
            "Screening persistence validation failed:\n- "
            "The expected evidence.json file was not written."
        )

    try:
        with open(evidence_file, "r", encoding="utf-8") as f:
            evidence_payload = json.load(f)
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"Unable to read valid evidence.json: {exc}") from exc

    if not isinstance(evidence_payload, dict):
        raise ValueError(
            "Screening persistence validation failed:\n- "
            "evidence.json root must be an object."
        )

    errors: list[str] = []
    try:
        evidence_by_index = _decisions_by_index(
            _extract_decisions_list(evidence_payload),
            source="evidence.json",
            expected_n_studies=expected_n_studies,
        )
    except ValueError as exc:
        raise ValueError(f"Screening persistence validation failed:\n- {exc}") from exc

    ordered = sorted(evidence_by_index.values(), key=lambda item: item["study_index"])
    errors.extend(
        _validate_counts(evidence_payload, ordered, source="evidence.json")
    )

    expected_indices = list(range(1, expected_n_studies + 1))
    if sorted(evidence_by_index) != expected_indices:
        missing = sorted(set(expected_indices) - set(evidence_by_index))
        extra = sorted(set(evidence_by_index) - set(expected_indices))
        errors.append(
            "evidence.json study_decisions do not cover expected indices "
            f"(missing={missing}, extra={extra})."
        )

    if errors:
        raise ValueError(
            "Screening persistence validation failed:\n- " + "\n- ".join(errors)
        )
