"""Build PRISMA flow counts from pipeline evidence (title/abstract stage)."""

from __future__ import annotations

import logging
from dataclasses import asdict, dataclass, field
from typing import Any

from bastirr.prisma.context import PrismaContext
from bastirr.prisma.flowchart import PrismaNewReviewCounts

logger = logging.getLogger(__name__)


@dataclass
class PrismaCountsMetadata:
    """PRISMA counts with pipeline metadata for counts.json."""

    review_type: str = "new"
    stages_completed: list[str] = field(
        default_factory=lambda: ["identification", "title_abstract_screening"]
    )
    limitations: list[str] = field(
        default_factory=lambda: [
            "No full-text retrieval; flowchart uses abstract-stage mapping",
        ]
    )
    databases: dict[str, int] = field(default_factory=dict)
    registers: int = 0
    duplicates_removed: int = 0
    ineligible_by_automation: int = 0
    removed_other_reasons: int = 0
    records_screened: int = 0
    records_excluded: int = 0
    reports_sought: int = 0
    reports_not_retrieved: int = 0
    reports_assessed: int = 0
    reports_excluded: dict[str, int] = field(default_factory=dict)
    studies_included: int = 0
    reports_included: int = 0
    validation_warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _count_decisions(evidence: dict[str, Any]) -> tuple[int, int, int]:
    decisions = evidence.get("screening_decisions", [])
    if not isinstance(decisions, list):
        return 0, 0, 0
    n_total = len(decisions)
    n_included = sum(
        1 for d in decisions
        if isinstance(d, dict) and str(d.get("decision", "")).upper() == "INCLUDE"
    )
    n_excluded = sum(
        1 for d in decisions
        if isinstance(d, dict) and str(d.get("decision", "")).upper() == "EXCLUDE"
    )
    return n_total, n_included, n_excluded


def build_prisma_counts(ctx: PrismaContext) -> PrismaCountsMetadata:
    """Map Bastirr title/abstract pipeline outputs to PRISMA flow numbers."""
    search_metadata = ctx.search_metadata
    n_candidates = int(search_metadata.get("num_candidates") or 0)
    n_total, n_included, n_excluded = _count_decisions(ctx.evidence)

    if not n_candidates and n_total:
        n_candidates = n_total

    source_name = "Cochrane benchmark dataset"
    if search_metadata.get("information_sources"):
        sources = search_metadata["information_sources"]
        if isinstance(sources, list) and sources:
            source_name = ", ".join(str(s) for s in sources)
        elif isinstance(sources, str):
            source_name = sources

    counts = PrismaCountsMetadata(
        databases={source_name: n_candidates},
        registers=0,
        duplicates_removed=0,
        ineligible_by_automation=0,
        removed_other_reasons=0,
        records_screened=n_candidates,
        records_excluded=n_excluded,
        reports_sought=n_included,
        reports_not_retrieved=0,
        reports_assessed=n_included,
        reports_excluded={},
        studies_included=n_included,
        reports_included=n_included,
    )

    flow_counts = _to_flowchart_counts(counts)
    counts.validation_warnings = flow_counts.validate()
    for warning in counts.validation_warnings:
        logger.warning("PRISMA counts: %s", warning)

    return counts


def _to_flowchart_counts(meta: PrismaCountsMetadata) -> PrismaNewReviewCounts:
    databases_total = sum(meta.databases.values())
    return PrismaNewReviewCounts(
        databases=databases_total,
        registers=meta.registers,
        duplicates_removed=meta.duplicates_removed,
        ineligible_by_automation=meta.ineligible_by_automation,
        removed_other_reasons=meta.removed_other_reasons,
        records_screened=meta.records_screened,
        records_excluded=meta.records_excluded,
        reports_sought=meta.reports_sought,
        reports_not_retrieved=meta.reports_not_retrieved,
        reports_assessed=meta.reports_assessed,
        reports_excluded=meta.reports_excluded,
        studies_included=meta.studies_included,
        reports_included=meta.reports_included,
    )
