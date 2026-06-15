"""Format structured search metadata for PRISMA checklist item 7."""

from __future__ import annotations

from typing import Any


def get_search_from_metadata(search_metadata: dict[str, Any]) -> dict[str, Any]:
    """Return structured search fields from ``search_metadata.json``."""
    search = search_metadata.get("search_strategy")
    if not isinstance(search, dict):
        return {}

    n_candidates = search.get("n_candidates")
    if n_candidates is not None:
        try:
            n_candidates = int(n_candidates)
        except (TypeError, ValueError):
            n_candidates = None

    return {
        "description": str(search.get("description", "")),
        "boolean_query": str(search.get("boolean_query", "")),
        "n_candidates": n_candidates,
    }


def format_search_strategy_for_checklist(
    search: dict[str, Any],
    *,
    information_sources: list[str] | str | None = None,
    num_candidates: int | None = None,
) -> str:
    """Render structured search metadata as PRISMA item 7 response text."""
    lines: list[str] = []

    if information_sources:
        if isinstance(information_sources, list):
            sources = ", ".join(str(s) for s in information_sources)
        else:
            sources = str(information_sources)
        lines.append(f"Information sources: {sources}")

    n = search.get("n_candidates")
    if n is None:
        n = num_candidates
    if n is not None:
        lines.append(f"Records identified: {n}")

    description = str(search.get("description", "")).strip()
    if description:
        if lines:
            lines.append("")
        lines.append("Search strategy:")
        lines.append(description)

    boolean_query = str(search.get("boolean_query", "")).strip()
    if boolean_query:
        if lines:
            lines.append("")
        lines.append("Boolean query:")
        lines.append(boolean_query)

    return "\n".join(lines).strip()
