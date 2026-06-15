"""Build PRISMA context from run artifacts and review protocol."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from bastirr.data import SystematicReview
from bastirr.prisma.search_strategy import get_search_from_metadata
from bastirr.search_metadata import load_search_metadata


@dataclass
class PrismaContext:
    """Aggregated inputs for PRISMA checklist and flowchart generation."""

    run_dir: Path
    title: str
    objective: str
    background: str
    selection_criteria: str
    evidence: dict[str, Any] = field(default_factory=dict)
    report_md: str = ""
    search_metadata: dict[str, Any] = field(default_factory=dict)
    candidate_titles: dict[int, str] = field(default_factory=dict)

    def to_llm_dict(self) -> dict[str, Any]:
        """Serialize context for LLM checklist fill (truncated where needed)."""
        return {
            "title": self.title,
            "objective": self.objective,
            "background": self.background[:3000] if self.background else "",
            "selection_criteria": self.selection_criteria[:2000] if self.selection_criteria else "",
            "num_candidates": self.search_metadata.get("num_candidates")
            or len(self.evidence.get("screening_decisions", [])),
            "search_strategy": _format_search_strategy_for_llm(self.search_metadata),
            "screening_decisions": self.evidence.get("screening_decisions", []),
            "synthesis": (self.evidence.get("synthesis") or "")[:4000],
            "quality_assessment": self.evidence.get("quality_assessment", []),
            "evidence_strength": self.evidence.get("evidence_strength", ""),
            "limitations": self.evidence.get("limitations", []),
            "evidence_summary": _summarize_evidence(self.evidence.get("evidence", [])),
            "report_excerpt": self.report_md[:4000] if self.report_md else "",
            "stages_completed": ["identification", "title_abstract_screening"],
            "limitations_note": (
                "Bastirr v1 pipeline completes title/abstract screening only; "
                "full-text retrieval is not performed."
            ),
        }


def _format_search_strategy_for_llm(search_metadata: dict[str, Any]) -> str:
    search = get_search_from_metadata(search_metadata)
    if search.get("description") or search.get("boolean_query"):
        parts: list[str] = []
        if search.get("description"):
            parts.append(str(search["description"]))
        if search.get("boolean_query"):
            parts.append(f"Boolean query: {search['boolean_query']}")
        return "\n".join(parts)[:2000]

    return ""


def _summarize_evidence(studies: list[Any]) -> list[dict[str, Any]]:
    summaries: list[dict[str, Any]] = []
    for study in studies[:10]:
        if not isinstance(study, dict):
            continue
        summaries.append({
            "study_index": study.get("study_index"),
            "citation": study.get("citation", ""),
            "study_design": study.get("study_design", ""),
            "population": str(study.get("population", ""))[:500],
            "intervention": str(study.get("intervention", ""))[:300],
            "key_findings": study.get("key_findings", [])[:5],
        })
    return summaries


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except (json.JSONDecodeError, OSError):
        return {}


def build_prisma_context(
    run_dir: Path,
    review: SystematicReview | None = None,
) -> PrismaContext:
    """Load run artifacts and review protocol into a :class:`PrismaContext`."""
    run_dir = Path(run_dir)
    evidence = _load_json(run_dir / "evidence.json")
    search_metadata = load_search_metadata(run_dir)

    report_path = run_dir / "report.md"
    report_md = report_path.read_text(encoding="utf-8") if report_path.exists() else ""

    candidate_titles: dict[int, str] = {}
    if review is not None:
        for i, study in enumerate(review.studies):
            candidate_titles[i + 1] = study.title

    if review is not None:
        title = review.title
        objective = review.objective
        background = review.background
        selection_criteria = review.selection_criteria
    else:
        title = search_metadata.get("title", "")
        objective = search_metadata.get("objective", "")
        background = search_metadata.get("background", "")
        selection_criteria = search_metadata.get("selection_criteria", "")

    return PrismaContext(
        run_dir=run_dir,
        title=title,
        objective=objective,
        background=background,
        selection_criteria=selection_criteria,
        evidence=evidence,
        report_md=report_md,
        search_metadata=search_metadata,
        candidate_titles=candidate_titles,
    )
