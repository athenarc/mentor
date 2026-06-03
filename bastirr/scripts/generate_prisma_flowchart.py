#!/usr/bin/env python3
"""Generate a PRISMA 2020 flow diagram image from numeric inputs.

This script targets the *new review* PRISMA 2020 layout shown in the official
template (identification -> screening -> included), matching the structure in:
https://www.prisma-statement.org/prisma-2020-flow-diagram

Third-party options investigated
--------------------------------
1. **PRISMA2020 (R package)** — Recommended official-quality output.
   - Interactive HTML + static PNG/PDF/SVG export via ``PRISMA_save()``.
   - Data-driven via CSV template; best visual fidelity.
   - Web app: https://prisma-flowdiagram.github.io/PRISMA2020/
   - Not Python-native; requires R runtime for automation.

2. **prisma-flow-diagram (PyPI)** — Python package built on matplotlib.
   - ``pip install -r bastirr/requirements-prisma.txt`` (includes **colrev**, required
     at import time even for count-driven plots).
   - Wrapper: ``bastirr/scripts/generate_prisma_flowchart_pypi.py`` (same JSON/CLI as
     this script).

3. **Graphviz / diagrams.net / BioRender** — Manual or semi-manual diagram tools.
   - Good for one-off figures; weaker for reproducible scripted pipelines.

4. **This script** — Lightweight, dependency-minimal Python renderer (matplotlib).
   - Good for CI/automation inside SR-agents without R.

Usage
-----
From JSON:

    python bastirr/scripts/generate_prisma_flowchart.py \\
      --input bastirr/scripts/examples/prisma_new_review.json \\
      --output prisma_flowchart.png

From CLI flags:

    python bastirr/scripts/generate_prisma_flowchart.py \\
      --databases 1250 --registers 340 \\
      --duplicates-removed 210 --ineligible-by-automation 45 --removed-other-reasons 12 \\
      --records-screened 1323 --records-excluded 1180 \\
      --reports-sought 143 --reports-not-retrieved 8 --reports-assessed 135 \\
      --reports-excluded "Wrong population:52,Wrong intervention:31" \\
      --studies-included 25 --reports-included 27 \\
      --output prisma_flowchart.png
"""

from __future__ import annotations

import argparse
import json
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

        return cls(
            databases=int(data.get("databases", 0)),
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


def _parse_reports_excluded_arg(value: str) -> dict[str, int]:
    """Parse ``Reason:12,Other:3`` style CLI values."""
    out: dict[str, int] = {}
    if not value.strip():
        return out
    for chunk in value.split(","):
        part = chunk.strip()
        if not part:
            continue
        if ":" not in part:
            raise ValueError(
                f"Invalid exclusion entry '{part}'. Expected format 'Reason:count'."
            )
        reason, count_raw = part.rsplit(":", 1)
        reason = reason.strip()
        if not reason:
            raise ValueError(f"Invalid exclusion entry '{part}': empty reason.")
        out[reason] = int(count_raw.strip())
    return out


def _box(
    ax,
    xy: tuple[float, float],
    width: float,
    height: float,
    text: str,
    *,
    facecolor: str = "white",
    edgecolor: str = "black",
    fontsize: float = 9,
    ha: str = "center",
    va: str = "center",
    fontweight: str | None = None,
    rounding: float | None = None,
) -> None:
    from matplotlib.patches import FancyBboxPatch, Rectangle

    x, y = xy
    if rounding:
        patch = FancyBboxPatch(
            (x, y),
            width,
            height,
            boxstyle=f"round,pad=0,rounding_size={rounding}",
            linewidth=1.2,
            edgecolor=edgecolor,
            facecolor=facecolor,
            zorder=2,
        )
    else:
        patch = Rectangle(
            (x, y),
            width,
            height,
            linewidth=1.2,
            edgecolor=edgecolor,
            facecolor=facecolor,
            zorder=2,
        )
    ax.add_patch(patch)
    ax.text(
        x + width / 2,
        y + height / 2,
        text,
        ha=ha,
        va=va,
        fontsize=fontsize,
        wrap=True,
        fontweight=fontweight,
        zorder=3,
    )


def _arrow(ax, start: tuple[float, float], end: tuple[float, float]) -> None:
    ax.annotate(
        "",
        xy=end,
        xytext=start,
        arrowprops=dict(arrowstyle="->", color="black", lw=1.2),
        zorder=1,
    )


def _arrow_horizontal(ax, x_start: float, x_end: float, y: float) -> None:
    """Draw a strictly horizontal arrow (constant y)."""
    _arrow(ax, (x_start, y), (x_end, y))


def _arrow_vertical(ax, x: float, y_start: float, y_end: float) -> None:
    """Draw a strictly vertical arrow (constant x)."""
    _arrow(ax, (x, y_start), (x, y_end))


def _box_center_y(y: float, height: float) -> float:
    return y + height / 2


def _phase_label(ax, y: float, height: float, text: str, *, rounding: float = 0.012) -> None:
    """Blue phase label with vertical text."""
    from matplotlib.patches import FancyBboxPatch

    x = 0.02
    width = 0.08
    patch = FancyBboxPatch(
        (x, y),
        width,
        height,
        boxstyle=f"round,pad=0,rounding_size={rounding}",
        linewidth=1.2,
        edgecolor="black",
        facecolor="#d9edf7",
        zorder=2,
    )
    ax.add_patch(patch)
    ax.text(
        x + width / 2,
        y + height / 2,
        text,
        rotation=90,
        ha="center",
        va="center",
        fontsize=10,
        fontweight="bold",
        zorder=3,
    )


def render_prisma_new_review(counts: PrismaNewReviewCounts, output_path: Path, *, dpi: int = 200) -> Path:
    """Render PRISMA 2020 new-review diagram to an image file."""
    import matplotlib.pyplot as plt

    fig_w, fig_h = 14, 16
    fig, ax = plt.subplots(figsize=(fig_w, fig_h))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    left_x = 0.12
    right_x = 0.58
    box_w = 0.34
    main_h = 0.085
    side_h = 0.11
    header_h = 0.045
    header_gap = 0.07
    header_y = 0.94
    body_top = header_y - header_gap

    # Yellow header at the top; diagram body starts below with a clear gap.
    _box(
        ax,
        (left_x, header_y),
        0.8,
        header_h,
        "Identification of studies via databases and registers",
        facecolor="#f7e08c",
        fontsize=11,
        fontweight="bold",
        rounding=0.012,
    )

    # Identification
    y = body_top - main_h
    _phase_label(ax, body_top - 0.14, 0.14, "Identification")
    _box(
        ax,
        (left_x, y),
        box_w,
        main_h,
        (
            "Records identified from*:\n"
            f"Databases (n = {counts.databases:,})\n"
            f"Registers (n = {counts.registers:,})"
        ),
        fontsize=9,
    )
    _box(
        ax,
        (right_x, y),
        box_w,
        side_h,
        (
            "Records removed before screening:\n"
            f"Duplicate records removed (n = {counts.duplicates_removed:,})\n"
            f"Records marked as ineligible by automation tools (n = {counts.ineligible_by_automation:,})\n"
            f"Records removed for other reasons (n = {counts.removed_other_reasons:,})"
        ),
        fontsize=8,
    )
    y_arrow = _box_center_y(y, main_h)
    _arrow_horizontal(ax, left_x + box_w, right_x, y_arrow)

    # Screening block
    y_screened = y - 0.14
    _box(ax, (left_x, y_screened), box_w, main_h, f"Records screened (n = {counts.records_screened:,})", fontsize=9)
    _box(ax, (right_x, y_screened), box_w, main_h, f"Records excluded** (n = {counts.records_excluded:,})", fontsize=9)
    _arrow_horizontal(ax, left_x + box_w, right_x, _box_center_y(y_screened, main_h))
    _arrow_vertical(ax, left_x + box_w / 2, body_top - main_h, y_screened + main_h)

    y_sought = y_screened - 0.14
    _box(
        ax,
        (left_x, y_sought),
        box_w,
        main_h,
        f"Reports sought for retrieval (n = {counts.reports_sought:,})",
        fontsize=9,
    )
    _box(
        ax,
        (right_x, y_sought),
        box_w,
        main_h,
        f"Reports not retrieved (n = {counts.reports_not_retrieved:,})",
        fontsize=9,
    )
    _arrow_horizontal(ax, left_x + box_w, right_x, _box_center_y(y_sought, main_h))
    _arrow_vertical(ax, left_x + box_w / 2, y_screened, y_sought + main_h)

    excluded_lines = [f"{reason} (n = {n:,})" for reason, n in counts.reports_excluded.items()]
    if not excluded_lines:
        excluded_lines = ["Reason 1 (n = 0)", "Reason 2 (n = 0)", "Reason 3 (n = 0)", "etc."]
    excluded_text = "Reports excluded:\n" + "\n".join(excluded_lines)
    excluded_h = max(side_h, 0.03 * len(excluded_lines) + 0.06)

    y_assessed = y_sought - 0.16
    _box(
        ax,
        (left_x, y_assessed),
        box_w,
        main_h,
        f"Reports assessed for eligibility (n = {counts.reports_assessed:,})",
        fontsize=9,
    )
    _box(ax, (right_x, y_assessed), box_w, excluded_h, excluded_text, fontsize=8)
    _arrow_horizontal(ax, left_x + box_w, right_x, _box_center_y(y_assessed, main_h))
    _arrow_vertical(ax, left_x + box_w / 2, y_sought, y_assessed + main_h)

    _phase_label(ax, y_assessed, (y_screened + main_h) - y_assessed, "Screening")

    # Included
    y_included = y_assessed - 0.16
    _phase_label(ax, y_included, main_h + 0.02, "Included")
    y = y_included
    _box(
        ax,
        (left_x, y),
        box_w,
        main_h + 0.02,
        (
            f"Studies included in review (n = {counts.studies_included:,})\n"
            f"Reports of included studies (n = {counts.reports_included:,})"
        ),
        fontsize=9,
    )
    _arrow_vertical(ax, left_x + box_w / 2, y_assessed, y + main_h + 0.02)

    output_path = output_path.expanduser().resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=dpi, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return output_path


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate a PRISMA 2020 new-review flow diagram image."
    )
    parser.add_argument("--input", type=Path, help="JSON file with PRISMA counts.")
    parser.add_argument("--output", type=Path, required=True, help="Output image path (.png/.pdf/.svg).")
    parser.add_argument("--dpi", type=int, default=200, help="Image DPI (default: 200).")
    parser.add_argument("--strict", action="store_true", help="Fail on consistency warnings.")

    parser.add_argument("--databases", type=int, default=0)
    parser.add_argument("--registers", type=int, default=0)
    parser.add_argument("--duplicates-removed", type=int, default=0)
    parser.add_argument("--ineligible-by-automation", type=int, default=0)
    parser.add_argument("--removed-other-reasons", type=int, default=0)
    parser.add_argument("--records-screened", type=int, default=0)
    parser.add_argument("--records-excluded", type=int, default=0)
    parser.add_argument("--reports-sought", type=int, default=0)
    parser.add_argument("--reports-not-retrieved", type=int, default=0)
    parser.add_argument("--reports-assessed", type=int, default=0)
    parser.add_argument(
        "--reports-excluded",
        default="",
        help="Comma-separated exclusion reasons as Reason:count (e.g. 'Wrong population:52,Wrong intervention:31').",
    )
    parser.add_argument("--studies-included", type=int, default=0)
    parser.add_argument("--reports-included", type=int, default=0)
    return parser


def _load_counts(args: argparse.Namespace) -> PrismaNewReviewCounts:
    if args.input:
        payload = json.loads(args.input.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise ValueError("Input JSON must be an object.")
        return PrismaNewReviewCounts.from_dict(payload)

    return PrismaNewReviewCounts(
        databases=args.databases,
        registers=args.registers,
        duplicates_removed=args.duplicates_removed,
        ineligible_by_automation=args.ineligible_by_automation,
        removed_other_reasons=args.removed_other_reasons,
        records_screened=args.records_screened,
        records_excluded=args.records_excluded,
        reports_sought=args.reports_sought,
        reports_not_retrieved=args.reports_not_retrieved,
        reports_assessed=args.reports_assessed,
        reports_excluded=_parse_reports_excluded_arg(args.reports_excluded),
        studies_included=args.studies_included,
        reports_included=args.reports_included,
    )


def main() -> int:
    parser = _build_arg_parser()
    args = parser.parse_args()
    counts = _load_counts(args)

    warnings = counts.validate()
    for warning in warnings:
        print(f"WARNING: {warning}")
    if warnings and args.strict:
        raise SystemExit(1)

    output = render_prisma_new_review(counts, args.output, dpi=args.dpi)
    print(f"Wrote PRISMA flowchart to {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
