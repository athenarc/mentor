"""Render excluded studies for PRISMA item 16b."""

from __future__ import annotations

from typing import Any

from bastirr.prisma.context import PrismaContext


def build_excluded_studies(ctx: PrismaContext) -> list[dict[str, Any]]:
    """Return excluded records at title/abstract screening from evidence.json."""
    decisions = ctx.evidence.get("screening_decisions", [])
    if not isinstance(decisions, list):
        decisions = []

    excluded = [
        d for d in decisions
        if isinstance(d, dict) and str(d.get("decision", "")).upper() == "EXCLUDE"
    ]
    excluded.sort(key=lambda d: int(d.get("study_index", 0)))

    records: list[dict[str, Any]] = []
    for d in excluded:
        idx = d.get("study_index", "?")
        title = ""
        if str(idx).isdigit():
            title = ctx.candidate_titles.get(int(idx), "")
        if not title:
            title = f"Study {idx}"
        records.append({
            "study_index": idx,
            "title": title,
            "reason": str(d.get("reason", "")),
            "decision": "EXCLUDE",
        })
    return records


def render_excluded_table(ctx: PrismaContext) -> str:
    """Build markdown listing records excluded at title/abstract screening."""
    records = build_excluded_studies(ctx)

    lines = [
        "# Excluded studies (title/abstract screening)",
        "",
        "Records excluded during title/abstract screening (PRISMA 2020 item 16b).",
        "",
        "| Study | Title | Reason |",
        "|-------|-------|--------|",
    ]

    if not records:
        lines.append("| — | — | No excluded records recorded. |")
    else:
        for row in records:
            idx = row["study_index"]
            title = str(row["title"]).replace("|", "\\|")
            reason = str(row["reason"]).replace("|", "\\|").replace("\n", " ")
            lines.append(f"| {idx} | {title[:120]} | {reason[:500]} |")

    lines.append("")
    return "\n".join(lines)


def render_excluded_json(ctx: PrismaContext) -> dict[str, Any]:
    """Build machine-readable excluded-studies payload for PRISMA item 16b."""
    return {
        "prisma_item": "16b",
        "stage": "title_abstract_screening",
        "source": "evidence.json screening_decisions",
        "excluded": build_excluded_studies(ctx),
    }
