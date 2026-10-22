"""
One-review domain types and JSON I/O for Mentor runs.

Mentor never loads the Cochrane CSV dataset. Callers (CLI or experiments)
provide a review JSON file matching ``review_to_json`` / ``load_review_from_json``.

Mode-dependent input contract (``mode`` defaults to ``full`` when omitted):
- ``screening-only`` — ``studies`` required (non-empty)
- ``full`` — protocol fields only; ``studies`` must be absent or empty
  (Librarian retrieves candidates)
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Literal

from mentor.agents.prompts import PROMPT_ROLES

# Gold labels are optional at run time (JSON inputs omit them).
LABEL_INCLUDED = 1.0
LABEL_UNKNOWN = -1.0

ReviewMode = Literal["full", "screening-only"]
VALID_MODES = frozenset({"full", "screening-only"})


@dataclass
class Study:
    """A single candidate study (title + abstract; optional gold label)."""

    title: str
    abstract: str
    label: float = LABEL_UNKNOWN

    @property
    def is_included(self) -> bool:
        return self.label == LABEL_INCLUDED


@dataclass
class SystematicReview:
    """A systematic review protocol plus candidate studies."""

    title: str
    background: str
    objective: str
    selection_criteria: str
    mode: ReviewMode
    studies: List[Study] = field(default_factory=list)
    # Role → absolute prompt file path. Missing roles use packaged defaults.
    prompts: Dict[str, str] = field(default_factory=dict)

    @property
    def included_studies(self) -> List[Study]:
        return [s for s in self.studies if s.is_included]

    @property
    def excluded_studies(self) -> List[Study]:
        return [s for s in self.studies if not s.is_included]

    def summary(self) -> str:
        override_roles = ", ".join(sorted(self.prompts)) or "(defaults)"
        return (
            f"Review: {self.title}\n"
            f"  Mode: {self.mode}\n"
            f"  Studies: {len(self.studies)} total, "
            f"{len(self.included_studies)} included, "
            f"{len(self.excluded_studies)} excluded\n"
            f"  Prompt overrides: {override_roles}\n"
            f"  Objective: {self.objective[:150]}..."
        )


def normalize_mode(raw: Any) -> ReviewMode:
    """Parse/normalize a mode value (``None``/empty → ``full``)."""
    if raw is None or (isinstance(raw, str) and not str(raw).strip()):
        return "full"
    key = str(raw).strip().lower()
    if key not in VALID_MODES:
        raise ValueError(
            f"Review JSON 'mode' must be one of {sorted(VALID_MODES)}, got {raw!r}"
        )
    return key  # type: ignore[return-value]


def _parse_mode(raw: Any) -> ReviewMode:
    return normalize_mode(raw)


def validate_review_for_mode(review: SystematicReview) -> None:
    """Enforce mode-dependent study requirements."""
    if review.mode == "screening-only":
        if not review.studies:
            raise ValueError(
                "mode=screening-only requires a non-empty 'studies' list "
                "in the review JSON."
            )
        return
    # mode == "full"
    if review.studies:
        raise ValueError(
            "mode=full expects protocol-only review JSON (no 'studies'). "
            "Omit studies and let the Librarian retrieve candidates, or use "
            "mode=screening-only."
        )


def _parse_prompts(
    raw: Any,
    *,
    base_dir: Path | None = None,
) -> dict[str, str]:
    """Parse optional ``prompts`` map; resolve relative paths against ``base_dir``."""
    if raw is None:
        return {}
    if not isinstance(raw, dict):
        raise ValueError("Review JSON 'prompts' must be an object of role → path.")
    base = (base_dir or Path.cwd()).resolve()
    out: dict[str, str] = {}
    unknown = sorted(str(k) for k in raw if str(k) not in PROMPT_ROLES)
    if unknown:
        raise ValueError(
            f"Unknown prompt role(s) {unknown}. "
            f"Allowed: {sorted(PROMPT_ROLES)}"
        )
    for role, path_raw in raw.items():
        role_key = str(role)
        path_str = str(path_raw or "").strip()
        if not path_str:
            raise ValueError(f"prompts.{role_key} must be a non-empty file path.")
        path = Path(path_str)
        if not path.is_absolute():
            path = (base / path).resolve()
        if not path.is_file():
            raise ValueError(f"prompts.{role_key} file not found: {path}")
        out[role_key] = str(path)
    return out


def review_to_json(review: SystematicReview) -> str:
    """Serialize review for Mentor / search store (no gold labels).

    Omits ``studies`` when empty so ``mode=full`` files stay protocol-only.
    Omits ``prompts`` (run-time only; not part of the search-store payload).
    """
    data: dict[str, Any] = {
        "mode": review.mode,
        "title": review.title,
        "objective": review.objective,
        "background": review.background,
        "selection_criteria": review.selection_criteria,
    }
    if review.studies:
        data["studies"] = [
            {
                "study_index": i + 1,
                "title": s.title,
                "abstract": s.abstract,
            }
            for i, s in enumerate(review.studies)
        ]
    return json.dumps(data, ensure_ascii=False)


def protocol_to_json(review: SystematicReview) -> str:
    """Protocol-only JSON for orchestrator task text (no candidate studies)."""
    data = {
        "title": review.title,
        "objective": review.objective,
        "background": review.background,
        "selection_criteria": review.selection_criteria,
    }
    return json.dumps(data, ensure_ascii=False)


def review_from_dict(
    data: dict[str, Any],
    *,
    base_dir: Path | None = None,
) -> SystematicReview:
    """Build a ``SystematicReview`` from a Mentor review JSON object."""
    if not isinstance(data, dict):
        raise ValueError("Review JSON root must be an object.")
    mode = _parse_mode(data.get("mode"))
    raw_studies = data.get("studies")
    if raw_studies is None:
        raw_studies = []
    if not isinstance(raw_studies, list):
        raise ValueError("Review JSON 'studies' must be a list when present.")
    studies: list[Study] = []
    for item in raw_studies:
        if not isinstance(item, dict):
            raise ValueError("Each study must be an object with title and abstract.")
        title = str(item.get("title") or "").strip()
        abstract = str(item.get("abstract") or "").strip()
        if not title and not abstract:
            raise ValueError("Each study needs a title or abstract.")
        label = item.get("label", LABEL_UNKNOWN)
        try:
            label_f = float(label)
        except (TypeError, ValueError):
            label_f = LABEL_UNKNOWN
        studies.append(Study(title=title, abstract=abstract, label=label_f))
    review = SystematicReview(
        title=str(data.get("title") or "").strip() or "Untitled review",
        background=str(data.get("background") or ""),
        objective=str(data.get("objective") or ""),
        selection_criteria=str(data.get("selection_criteria") or ""),
        mode=mode,
        studies=studies,
        prompts=_parse_prompts(data.get("prompts"), base_dir=base_dir),
    )
    validate_review_for_mode(review)
    return review


def load_review_from_json(path: str | Path) -> SystematicReview:
    """Load one systematic review from a Mentor review JSON file."""
    path = Path(path)
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    return review_from_dict(data, base_dir=path.parent)
