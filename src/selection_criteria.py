"""Structured IC/EC selection criteria for review JSON inputs."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, List

_IC_ID = re.compile(r"^IC\d+$", re.IGNORECASE)
_EC_ID = re.compile(r"^EC\d+$", re.IGNORECASE)
_SELECTION_CRITERIA_KEYS = frozenset({"inclusion", "exclusion"})
_CRITERION_KEYS = frozenset({"id", "text"})


@dataclass(frozen=True)
class Criterion:
    """One inclusion or exclusion criterion from the review protocol."""

    id: str
    text: str


@dataclass(frozen=True)
class SelectionCriteria:
    """Structured eligibility criteria (IC/EC lists; no free-text blob)."""

    inclusion: List[Criterion]
    exclusion: List[Criterion]

    def to_dict(self) -> dict[str, Any]:
        return {
            "inclusion": [
                {"id": item.id, "text": item.text} for item in self.inclusion
            ],
            "exclusion": [
                {"id": item.id, "text": item.text} for item in self.exclusion
            ],
        }

    def format_text(self) -> str:
        """Human-readable checklist for prompts and logs."""
        lines: list[str] = []
        if self.inclusion:
            lines.append("Inclusion criteria:")
            for item in self.inclusion:
                lines.append(f"- {item.id}: {item.text}")
        if self.exclusion:
            if lines:
                lines.append("")
            lines.append("Exclusion criteria:")
            for item in self.exclusion:
                lines.append(f"- {item.id}: {item.text}")
        return "\n".join(lines)

    def criterion_ids(self) -> list[str]:
        return [item.id for item in self.inclusion] + [
            item.id for item in self.exclusion
        ]


def parse_selection_criteria(raw: Any) -> SelectionCriteria:
    """Parse and validate structured ``selection_criteria`` from review JSON.

    Free-text strings are rejected. Either ``inclusion`` or ``exclusion`` may
    be omitted or empty, but at least one criterion is required::

        {
          "inclusion": [{"id": "IC1", "text": "..."}, ...],
          "exclusion": [{"id": "EC1", "text": "..."}, ...]
        }
    """
    if isinstance(raw, str):
        raise ValueError(
            "selection_criteria must be an object with optional 'inclusion' "
            "and/or 'exclusion' lists; free-text strings are not accepted."
        )
    if not isinstance(raw, dict):
        raise ValueError(
            "selection_criteria must be an object with optional 'inclusion' "
            f"and/or 'exclusion' lists; got {type(raw).__name__}."
        )
    unknown = sorted(str(key) for key in raw if str(key) not in _SELECTION_CRITERIA_KEYS)
    if unknown:
        raise ValueError(
            "selection_criteria has unknown key(s) "
            f"{unknown}; allowed: {sorted(_SELECTION_CRITERIA_KEYS)}."
        )
    if "inclusion" not in raw and "exclusion" not in raw:
        raise ValueError(
            "selection_criteria must include at least one of 'inclusion' or "
            "'exclusion'."
        )

    inclusion = _parse_criterion_list(
        raw.get("inclusion"),
        field_name="inclusion",
        id_pattern=_IC_ID,
        id_kind="IC",
    )
    exclusion = _parse_criterion_list(
        raw.get("exclusion"),
        field_name="exclusion",
        id_pattern=_EC_ID,
        id_kind="EC",
    )
    if not inclusion and not exclusion:
        raise ValueError(
            "selection_criteria must contain at least one inclusion or "
            "exclusion criterion."
        )

    ids = [item.id for item in inclusion] + [item.id for item in exclusion]
    duplicates = sorted({item_id for item_id in ids if ids.count(item_id) > 1})
    if duplicates:
        raise ValueError(
            f"selection_criteria has duplicate criterion id(s): {duplicates}."
        )
    return SelectionCriteria(inclusion=inclusion, exclusion=exclusion)


def _parse_criterion_list(
    raw: Any,
    *,
    field_name: str,
    id_pattern: re.Pattern[str],
    id_kind: str,
) -> list[Criterion]:
    if raw is None:
        return []
    if not isinstance(raw, list):
        raise ValueError(
            f"selection_criteria.{field_name} must be a list when present; "
            f"got {type(raw).__name__}."
        )
    criteria: list[Criterion] = []
    for index, item in enumerate(raw, start=1):
        location = f"selection_criteria.{field_name}[{index}]"
        if not isinstance(item, dict):
            raise ValueError(f"{location} must be an object with 'id' and 'text'.")
        unknown = sorted(str(key) for key in item if str(key) not in _CRITERION_KEYS)
        if unknown:
            raise ValueError(
                f"{location} has unknown key(s) {unknown}; "
                f"allowed: {sorted(_CRITERION_KEYS)}."
            )
        if "id" not in item or "text" not in item:
            raise ValueError(f"{location} must contain 'id' and 'text'.")
        criterion_id = str(item.get("id") or "").strip().upper()
        text = str(item.get("text") or "").strip()
        if not criterion_id:
            raise ValueError(f"{location}.id must be a non-empty string.")
        if not id_pattern.fullmatch(criterion_id):
            raise ValueError(
                f"{location}.id must match {id_kind}<number> "
                f"(e.g. {id_kind}1); got {item.get('id')!r}."
            )
        if not text:
            raise ValueError(f"{location}.text must be a non-empty string.")
        criteria.append(Criterion(id=criterion_id, text=text))
    return criteria
