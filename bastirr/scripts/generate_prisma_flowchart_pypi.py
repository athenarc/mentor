#!/usr/bin/env python3
"""Generate a PRISMA 2020 new-review flow diagram using prisma-flow-diagram (PyPI).

Keeps the standalone matplotlib renderer in ``generate_prisma_flowchart.py``.
This script maps the same JSON/CLI counts into the nested schema expected by
``plot_prisma2020_new`` from https://pypi.org/project/prisma-flow-diagram/

Requires optional dependencies (see ``bastirr/requirements-prisma.txt``):

    pip install -r bastirr/requirements-prisma.txt

Usage
-----
    python bastirr/scripts/generate_prisma_flowchart_pypi.py \\
      --input bastirr/scripts/examples/prisma_new_review.json \\
      --output prisma_flowchart_pypi.png
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt

from generate_prisma_flowchart import PrismaNewReviewCounts, _build_arg_parser, _load_counts


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

    removed: dict[str, int] = {}
    if counts.duplicates_removed:
        removed["duplicates"] = counts.duplicates_removed
    if counts.ineligible_by_automation:
        removed["automation"] = counts.ineligible_by_automation
    if counts.removed_other_reasons:
        removed["other"] = counts.removed_other_reasons
    if removed:
        db_registers["removed_before_screening"] = removed

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


def _render_prisma2020_new_fitted(
    *,
    db_registers: dict[str, Any],
    included: dict[str, Any],
    output_path: Path,
    figsize_width: float = 14.0,
    dpi: int = 300,
    validation: str = "warn",
) -> None:
    """Render via prisma-flow-diagram with ylim/figsize fitted to drawn content.

    The upstream ``plot_prisma2020_new`` keeps a fixed data ylim of (0, 9) on a
    landscape canvas, which leaves a large empty band below the diagram. That
    happens with both pandas 2 and 3; this path tightens the axes like the
    library already does for *updated* review layouts.
    """
    from prisma_flow_diagram.prisma import MatplotlibRenderer, Prisma2020Diagram
    from prisma_flow_diagram.validation import handle_validation

    diagram = Prisma2020Diagram(
        db_registers=db_registers,
        included=included,
        other_methods=None,
        previous=None,
        new_db_registers=None,
        new_included=None,
    )

    if validation != "off":
        issues = diagram.validate()
        handle_validation(issues, mode=validation)

    texts = diagram._build_text_blocks()
    has_other = texts.other_left is not None and texts.other_right is not None
    widths = diagram._compute_widths(texts)
    layout = diagram._compute_layout(widths, has_other=has_other)
    style = diagram.style

    renderer = MatplotlibRenderer(
        figsize=(figsize_width, 10.0), style=style, xlim=layout.xlim
    )
    diagram._draw_headers(renderer, layout, has_other=has_other)
    lanes = diagram._draw_lanes(
        renderer=renderer, layout=layout, widths=widths, texts=texts
    )
    included_geoms = diagram._draw_included(
        renderer=renderer, layout=layout, widths=widths, texts=texts, lanes=lanes
    )
    diagram._draw_phase_labels(
        renderer=renderer, lanes=lanes, included=included_geoms
    )

    ymin = style.ylim[0]
    ymax = style.header_y + style.header_h / 2 + 0.25
    if included_geoms.included is not None:
        ymin = min(ymin, included_geoms.included.bottom - style.bottom_padding)
    elif included_geoms.total is not None:
        ymin = min(ymin, included_geoms.total.bottom - style.bottom_padding)

    renderer.ax.set_ylim(ymin, ymax)

    x_span = max(1.0, layout.xlim[1] - layout.xlim[0])
    data_aspect = (ymax - ymin) / x_span
    renderer.fig.set_size_inches(figsize_width, figsize_width * data_aspect, forward=True)

    renderer.fig.savefig(
        output_path,
        bbox_inches="tight",
        dpi=dpi,
        pad_inches=0.05,
        facecolor="white",
    )
    plt.close(renderer.fig)


def render_prisma_pypi(
    counts: PrismaNewReviewCounts,
    output_path: Path,
    *,
    strict_validation: bool = False,
    fit_height: bool = True,
    figsize_width: float = 14.0,
    dpi: int = 300,
) -> Path:
    try:
        from prisma_flow_diagram.prisma import PrismaStyle
    except ImportError as exc:
        raise SystemExit(
            "prisma-flow-diagram is not installed. Run:\n"
            "  pip install -r bastirr/requirements-prisma.txt"
        ) from exc

    db_registers, included = counts_to_pypi_payload(counts)
    validation = "error" if strict_validation else "warn"
    output_path = output_path.expanduser().resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if fit_height:
        _render_prisma2020_new_fitted(
            db_registers=db_registers,
            included=included,
            output_path=output_path,
            figsize_width=figsize_width,
            dpi=dpi,
            validation=validation,
        )
        return output_path

    from prisma_flow_diagram import plot_prisma2020_new

    plot_prisma2020_new(
        db_registers=db_registers,
        included=included,
        filename=str(output_path),
        validation=validation,
        figsize=(figsize_width, 10.0),
        style=PrismaStyle(),
    )
    return output_path


def main() -> int:
    parser = _build_arg_parser()
    parser.description = (
        "Generate a PRISMA 2020 new-review flow diagram (prisma-flow-diagram backend)."
    )
    parser.add_argument(
        "--no-fit-height",
        action="store_true",
        help="Use upstream plot_prisma2020_new sizing (fixed ylim 0–9, may leave bottom whitespace).",
    )
    parser.add_argument(
        "--figsize-width",
        type=float,
        default=14.0,
        help="Figure width in inches when --fit-height is used (default: 14).",
    )
    args = parser.parse_args()
    counts = _load_counts(args)

    warnings = counts.validate()
    for warning in warnings:
        print(f"WARNING: {warning}")
    if warnings and args.strict:
        raise SystemExit(1)

    output = render_prisma_pypi(
        counts,
        args.output,
        strict_validation=args.strict,
        fit_height=not args.no_fit_height,
        figsize_width=args.figsize_width,
        dpi=args.dpi,
    )
    print(f"Wrote PRISMA flowchart (pypi) to {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
