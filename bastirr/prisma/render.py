"""Render filled PRISMA checklist to Markdown."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class FilledChecklistItem:
    id: str
    section: str
    label: str
    description: str
    fill_mode: str
    response: str
    source: str
    structured_response: dict[str, Any] | None = None


def render_checklist_markdown(items: list[FilledChecklistItem], *, title: str = "") -> str:
    """Render checklist as a Markdown table."""
    lines = [
        "# PRISMA 2020 Checklist",
        "",
    ]
    if title:
        lines.extend([f"**Review:** {title}", ""])
    lines.extend([
        "| Section | Item | Checklist item | Response |",
        "|---------|------|----------------|----------|",
    ])

    for item in items:
        section = item.section.replace("|", "\\|")
        label = f"{item.id}. {item.label}".replace("|", "\\|")
        description = item.description.replace("|", "\\|").replace("\n", " ")
        response = (item.response or "").replace("|", "\\|").replace("\n", " ")
        if not response:
            response = "—"
        lines.append(f"| {section} | {label} | {description} | {response} |")

    lines.append("")
    return "\n".join(lines)
