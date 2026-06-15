"""Orchestrate PRISMA artifact generation for a Bastirr run."""

from __future__ import annotations

import json
import logging
from dataclasses import asdict
from pathlib import Path
from typing import Any

from bastirr.data import SystematicReview
from bastirr.prisma.context import build_prisma_context
from bastirr.prisma.counts import build_prisma_counts
from bastirr.prisma.excluded import render_excluded_json, render_excluded_table
from bastirr.prisma.fill_checklist import fill_checklist
from bastirr.prisma.flowchart import PrismaNewReviewCounts, render_flowchart
from bastirr.prisma.render import render_checklist_markdown

logger = logging.getLogger(__name__)


def generate_prisma_bundle(
    run_dir: Path | str,
    review: SystematicReview | None = None,
    model: Any = None,
) -> Path:
    """Generate PRISMA checklist, counts, flowchart, and excluded studies.

    Writes artifacts under ``<run_dir>/prisma/``.

    Args:
        run_dir: Path to the Bastirr run output directory.
        review: Optional review protocol (for candidate titles and protocol fields).
        model: Optional smolagents model for LLM checklist fill.

    Returns:
        Path to the ``prisma/`` output directory.
    """
    run_dir = Path(run_dir)
    prisma_dir = run_dir / "prisma"
    prisma_dir.mkdir(parents=True, exist_ok=True)

    ctx = build_prisma_context(run_dir, review)
    counts = build_prisma_counts(ctx)

    counts_path = prisma_dir / "counts.json"
    counts_path.write_text(
        json.dumps(counts.to_dict(), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    excluded_md = render_excluded_table(ctx)
    (prisma_dir / "excluded_studies.md").write_text(excluded_md, encoding="utf-8")
    (prisma_dir / "excluded_studies.json").write_text(
        json.dumps(render_excluded_json(ctx), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    try:
        flow_counts = PrismaNewReviewCounts.from_dict(counts.to_dict())
        render_flowchart(flow_counts, prisma_dir / "flowchart.png")
    except ImportError:
        logger.warning(
            "prisma-flow-diagram not installed; skipping flowchart.png "
            "(pip install -r bastirr/requirements-prisma.txt)"
        )
    except Exception as exc:
        logger.warning("PRISMA flowchart generation failed: %s", exc)

    filled = fill_checklist(ctx, counts, model=model)

    checklist_md = render_checklist_markdown(filled, title=ctx.title)
    (prisma_dir / "checklist.md").write_text(checklist_md, encoding="utf-8")

    checklist_json = []
    for item in filled:
        row = asdict(item)
        if row.get("structured_response") is None:
            row.pop("structured_response", None)
        checklist_json.append(row)
    (prisma_dir / "checklist.json").write_text(
        json.dumps(checklist_json, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    logger.info("PRISMA bundle written to %s", prisma_dir)
    return prisma_dir
