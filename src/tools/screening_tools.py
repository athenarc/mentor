"""
Prompt-formatting and decision tools for Gatekeeper screening.

These tools do not call an LLM themselves; they format the payload and
apply deterministic final-decision rules from per-criterion labels.
"""

from __future__ import annotations

import json
from typing import Any, Literal

from smolagents import tool

_CORE_STUDY_FIELDS = ("study_index", "title", "abstract")

FinalDecision = Literal["INCLUDE", "EXCLUDE", "UNCLEAR"]

_INCLUSION_LABELS = frozenset({"MET", "NOT_MET", "UNCLEAR"})
_EXCLUSION_LABELS = frozenset({"TRIGGERED", "NOT_TRIGGERED", "UNCLEAR"})


def _format_metadata_value(value: Any) -> str:
    if isinstance(value, (list, dict)):
        return json.dumps(value, ensure_ascii=False)
    return str(value)


def _criterion_kind(assessment: dict[str, Any]) -> Literal["inclusion", "exclusion"]:
    raw_type = assessment.get("type", assessment.get("kind"))
    if isinstance(raw_type, str):
        normalized = raw_type.strip().lower()
        if normalized in {"inclusion", "include", "ic"}:
            return "inclusion"
        if normalized in {"exclusion", "exclude", "ec"}:
            return "exclusion"

    criterion_id = str(assessment.get("id", "")).strip().upper()
    if criterion_id.startswith("IC"):
        return "inclusion"
    if criterion_id.startswith("EC"):
        return "exclusion"
    raise ValueError(
        "Each criterion assessment needs a kind (inclusion/exclusion) or an "
        f"id starting with IC/EC; got id={assessment.get('id')!r}, "
        f"type={assessment.get('type')!r}."
    )


def compute_final_decision(criteria: list[dict[str, Any]]) -> FinalDecision:
    """
    Assign INCLUDE | EXCLUDE | UNCLEAR from per-criterion labels.

    Rules, in order:
    1. EXCLUDE if any inclusion criterion is NOT_MET or any exclusion
       criterion is TRIGGERED.
    2. INCLUDE if all inclusion criteria are MET and all exclusion criteria
       are NOT_TRIGGERED.
    3. UNCLEAR otherwise.
    """
    if not isinstance(criteria, list) or not criteria:
        raise ValueError("criteria must be a non-empty list of assessments.")

    inclusion_labels: list[str] = []
    exclusion_labels: list[str] = []

    for position, raw in enumerate(criteria, start=1):
        if not isinstance(raw, dict):
            raise ValueError(
                f"Criterion assessment at position {position} must be an object."
            )
        label = str(raw.get("label", "")).strip().upper()
        kind = _criterion_kind(raw)
        if kind == "inclusion":
            if label not in _INCLUSION_LABELS:
                raise ValueError(
                    f"Invalid inclusion label {label!r} for criterion "
                    f"{raw.get('id')!r}; expected MET, NOT_MET, or UNCLEAR."
                )
            inclusion_labels.append(label)
        else:
            if label not in _EXCLUSION_LABELS:
                raise ValueError(
                    f"Invalid exclusion label {label!r} for criterion "
                    f"{raw.get('id')!r}; expected TRIGGERED, NOT_TRIGGERED, "
                    "or UNCLEAR."
                )
            exclusion_labels.append(label)

    if any(label == "NOT_MET" for label in inclusion_labels) or any(
        label == "TRIGGERED" for label in exclusion_labels
    ):
        return "EXCLUDE"

    if all(label == "MET" for label in inclusion_labels) and all(
        label == "NOT_TRIGGERED" for label in exclusion_labels
    ):
        return "INCLUDE"

    return "UNCLEAR"


@tool
def format_screening_tasks(candidates_json: str) -> str:
    """
    Format the screening payload for Gatekeeper criterion assessment.

    Returns a formatted list of studies with the selection criteria, ready
    for the Gatekeeper agent to make decisions on each. Pass a single study
    in ``studies`` for one-at-a-time screening. Any extra study fields beyond
    title/abstract (e.g. journal, year) are included when present.

    Args:
        candidates_json: JSON string with candidate studies. Must contain
            keys 'studies' (list), 'title', and 'selection_criteria'.

    Returns:
        A formatted string with all studies and criteria, requesting
        a structured screening decision for each.
    """
    review = json.loads(candidates_json)
    criteria = review.get("selection_criteria", "N/A")
    studies = review.get("studies", [])

    lines = [
        "=== SCREENING TASK ===",
        f"Review: {review.get('title', 'N/A')}",
        f"Total studies to screen: {len(studies)}",
        "",
        "SELECTION CRITERIA:",
        f"{criteria}",
        "",
        "INSTRUCTIONS: For each study below, assess every inclusion and "
        "exclusion criterion, then call get_final_decision for that study.",
        "Return exactly one decision object per study; do not omit studies.",
        "",
    ]

    for i, study in enumerate(studies):
        if not isinstance(study, dict):
            study = {}
        study_index = study.get("study_index", i + 1)
        title = study.get("title", "No title")
        abstract = study.get("abstract", "No abstract")
        lines.append(f"--- Study {study_index} ---")
        lines.append(f"Title: {title}")
        lines.append(f"Abstract: {abstract}")
        for key, value in study.items():
            if key in _CORE_STUDY_FIELDS:
                continue
            if value is None or value == "":
                continue
            lines.append(f"{key}: {_format_metadata_value(value)}")
        lines.append("")

    return "\n".join(lines)


@tool
def get_final_decision(criteria_json: str) -> str:
    """
    Return a deterministic INCLUDE | EXCLUDE | UNCLEAR from criterion labels.

    Call once per study after every inclusion and exclusion criterion has a
    label. Do not invent or override this tool's result.

    Args:
        criteria_json: JSON array of criterion assessments. Each object must
            include ``id`` (e.g. IC1, EC1) and ``label``. Inclusion labels:
            MET, NOT_MET, UNCLEAR. Exclusion labels: TRIGGERED,
            NOT_TRIGGERED, UNCLEAR. Optional ``type``/``kind`` may be
            ``inclusion`` or ``exclusion``; otherwise IC*/EC* ids are used.

    Returns:
        Exactly one of: INCLUDE, EXCLUDE, UNCLEAR.
    """
    try:
        criteria = json.loads(criteria_json)
    except json.JSONDecodeError as exc:
        raise ValueError("criteria_json must be valid JSON.") from exc
    if isinstance(criteria, dict) and "criteria" in criteria:
        criteria = criteria["criteria"]
    return compute_final_decision(criteria)
