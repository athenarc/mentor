"""PRISMA 2020 new-review flow diagram via prisma-flow-diagram (PyPI)."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class PrismaNewReviewCounts:
    """Counts for PRISMA 2020 new-review flow diagram."""

    databases: int = 0
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

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "PrismaNewReviewCounts":
        excluded_raw = data.get("reports_excluded", {})
        if isinstance(excluded_raw, dict):
            reports_excluded = {str(k): int(v) for k, v in excluded_raw.items()}
        elif isinstance(excluded_raw, list):
            reports_excluded = {}
            for item in excluded_raw:
                if not isinstance(item, dict):
                    continue
                reason = str(item.get("reason", "")).strip()
                count = int(item.get("count", 0))
                if reason:
                    reports_excluded[reason] = count
        else:
            reports_excluded = {}

        databases_val = data.get("databases", 0)
        if isinstance(databases_val, dict):
            databases_total = sum(int(v) for v in databases_val.values())
        else:
            databases_total = int(databases_val)

        return cls(
            databases=databases_total,
            registers=int(data.get("registers", 0)),
            duplicates_removed=int(data.get("duplicates_removed", 0)),
            ineligible_by_automation=int(data.get("ineligible_by_automation", 0)),
            removed_other_reasons=int(data.get("removed_other_reasons", 0)),
            records_screened=int(data.get("records_screened", 0)),
            records_excluded=int(data.get("records_excluded", 0)),
            reports_sought=int(data.get("reports_sought", 0)),
            reports_not_retrieved=int(data.get("reports_not_retrieved", 0)),
            reports_assessed=int(data.get("reports_assessed", 0)),
            reports_excluded=reports_excluded,
            studies_included=int(data.get("studies_included", 0)),
            reports_included=int(data.get("reports_included", 0)),
        )

    def validate(self) -> list[str]:
        """Return non-fatal consistency warnings."""
        warnings: list[str] = []
        identified = self.databases + self.registers
        removed_before_screening = (
            self.duplicates_removed
            + self.ineligible_by_automation
            + self.removed_other_reasons
        )
        expected_screened = identified - removed_before_screening
        if identified and self.records_screened != expected_screened:
            warnings.append(
                "records_screened does not equal identified minus removed-before-screening "
                f"({self.records_screened} vs {expected_screened})"
            )
        expected_sought = self.records_screened - self.records_excluded
        if self.records_screened and self.reports_sought != expected_sought:
            warnings.append(
                "reports_sought does not equal screened minus excluded "
                f"({self.reports_sought} vs {expected_sought})"
            )
        expected_assessed = self.reports_sought - self.reports_not_retrieved
        if self.reports_sought and self.reports_assessed != expected_assessed:
            warnings.append(
                "reports_assessed does not equal sought minus not-retrieved "
                f"({self.reports_assessed} vs {expected_assessed})"
            )
        excluded_total = sum(self.reports_excluded.values())
        expected_included_reports = self.reports_assessed - excluded_total
        if self.reports_assessed and self.reports_included != expected_included_reports:
            warnings.append(
                "reports_included does not equal assessed minus excluded reasons "
                f"({self.reports_included} vs {expected_included_reports})"
            )
        return warnings


def counts_to_pypi_payload(
    counts: PrismaNewReviewCounts,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Map flat PRISMA counts to prisma-flow-diagram db_registers + included."""
    db_registers: dict[str, Any] = {}

    identification: dict[str, int] = {}
    if counts.databases:
        identification["databases"] = counts.databases
    if counts.registers:
        identification["registers"] = counts.registers
    if identification:
        db_registers["identification"] = identification

    db_registers["removed_before_screening"] = {
        "duplicates": counts.duplicates_removed,
        "automation": counts.ineligible_by_automation,
        "other": counts.removed_other_reasons,
    }

    records: dict[str, int] = {}
    if counts.records_screened:
        records["screened"] = counts.records_screened
    if counts.records_excluded:
        records["excluded"] = counts.records_excluded
    if records:
        db_registers["records"] = records

    reports: dict[str, Any] = {}
    if counts.reports_sought:
        reports["sought"] = counts.reports_sought
    if counts.reports_not_retrieved:
        reports["not_retrieved"] = counts.reports_not_retrieved
    if counts.reports_assessed:
        reports["assessed"] = counts.reports_assessed
    if counts.reports_excluded:
        reports["excluded_reasons"] = {
            str(k): int(v) for k, v in counts.reports_excluded.items()
        }
    if reports:
        db_registers["reports"] = reports

    included: dict[str, int] = {}
    if counts.studies_included:
        included["studies"] = counts.studies_included
    if counts.reports_included:
        included["reports"] = counts.reports_included

    return db_registers, included


def render_flowchart(
    counts: PrismaNewReviewCounts | dict[str, Any],
    output_path: Path,
    *,
    strict_validation: bool = False,
) -> Path:
    """Render PRISMA 2020 new-review diagram using prisma-flow-diagram."""
    if isinstance(counts, dict):
        flow_counts = PrismaNewReviewCounts.from_dict(counts)
    else:
        flow_counts = counts

    try:
        from prisma_flow_diagram.prisma import PrismaStyle, plot_prisma2020_new
    except ImportError as exc:
        raise ImportError(
            "prisma-flow-diagram is not installed. Run:\n"
            "  pip install -r bastirr/requirements-prisma.txt"
        ) from exc

    db_registers, included = counts_to_pypi_payload(flow_counts)
    validation = "error" if strict_validation else "warn"
    output_path = Path(output_path).expanduser().resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    plot_prisma2020_new(
        db_registers=db_registers,
        included=included,
        filename=str(output_path),
        validation=validation,
        figsize=(14.0, 10.0),
        style=PrismaStyle(),
    )
    return output_path
