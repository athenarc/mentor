"""
Search & retrieval tools for the Librarian agent.

In the full Bastirr system, the Librarian would query PubMed, OpenAIRE, etc.
For this scaffolding, it retrieves candidate studies from a pre-loaded
study database — simulating a search by returning title + abstract records.

Call ``load_review_data(json_str)`` once (from the runner) before any
agent tools are invoked.  The tools read from the module-level store.
"""

import json

from smolagents import tool


# ---------------------------------------------------------------------------
# Module-level study store  (populated by the runner before the pipeline)
# ---------------------------------------------------------------------------
_review_data: dict | None = None


def load_review_data(review_data_json: str) -> None:
    """Load review data into the module-level store.

    This is called once by ``run_demo.py`` (or any runner) **before** the
    pipeline starts.  All librarian tools read from this store, simulating
    a database that the librarian can query.

    Args:
        review_data_json: Full JSON string with keys ``title``, ``objective``,
            ``background``, ``selection_criteria``, and ``studies``.
    """
    global _review_data
    _review_data = json.loads(review_data_json)


# ---------------------------------------------------------------------------
# Tools for the Librarian agent
# ---------------------------------------------------------------------------

@tool
def search_studies(query: str) -> str:
    """
    Search for candidate studies relevant to a systematic review question.
    In this scaffolding version, it returns all candidate studies from the
    pre-loaded study database (simulating a real database search).

    Args:
        query: The research question or search query.

    Returns:
        A formatted string listing all candidate studies with their index,
        title, and abstract (truncated).
    """
    if _review_data is None:
        return "ERROR: No review data loaded. The runner must call load_review_data() first."

    studies = _review_data.get("studies", [])

    lines = [
        f"Search results for: {query}",
        f"Found {len(studies)} candidate studies.",
        f"Review: {_review_data.get('title', 'N/A')}",
        f"Selection criteria: {_review_data.get('selection_criteria', 'N/A')}",
        "",
    ]

    for i, study in enumerate(studies):
        title = study.get("title", "No title")
        abstract = study.get("abstract", "No abstract")
        # Truncate abstract for readability
        abstract_preview = abstract[:300] + "..." if len(abstract) > 300 else abstract
        lines.append(f"--- Study {i + 1} ---")
        lines.append(f"Title: {title}")
        lines.append(f"Abstract: {abstract_preview}")
        lines.append("")

    return "\n".join(lines)


@tool
def get_review_protocol() -> str:
    """
    Extract the review protocol (objective, background, selection criteria)
    from the loaded review data.  The Librarian uses this to formulate
    search strategies.

    Returns:
        A formatted string with the review protocol details.
    """
    if _review_data is None:
        return "ERROR: No review data loaded."

    return (
        f"=== REVIEW PROTOCOL ===\n"
        f"Title: {_review_data.get('title', 'N/A')}\n\n"
        f"Background:\n{_review_data.get('background', 'N/A')}\n\n"
        f"Objective:\n{_review_data.get('objective', 'N/A')}\n\n"
        f"Selection Criteria:\n{_review_data.get('selection_criteria', 'N/A')}\n"
    )


# ---------------------------------------------------------------------------
# Tool for the Orchestrator — retrieves candidates after the librarian runs
# ---------------------------------------------------------------------------

@tool
def get_candidates_json() -> str:
    """
    Return all candidate studies found by the librarian as a clean JSON
    string.  The orchestrator calls this after the librarian finishes to
    obtain a structured candidate list for the gatekeeper.

    The returned JSON has the same schema used by the screening and
    report tools: ``{"title": ..., "selection_criteria": ..., "studies": [...]}``.

    Returns:
        A JSON string with the candidate studies and review metadata.
    """
    if _review_data is None:
        return "{}"
    return json.dumps(_review_data, ensure_ascii=False)
