"""
Search & retrieval tools for the Librarian agent.

In the full Bastirr system, the Librarian would query PubMed, OpenAIRE, etc.
For this scaffolding, it retrieves candidate studies from a pre-loaded
study database — simulating a search by returning title + abstract records.

Call ``load_review_data(json_str, output_dir=...)`` once (from the runner)
before any agent tools are invoked.
"""

import json
from dataclasses import dataclass

from smolagents import tool

from bastirr.search_metadata import update_search_strategy


@dataclass
class _RunContext:
    review_data: dict | None = None
    output_dir: str | None = None


_run = _RunContext()


def load_review_data(review_data_json: str, *, output_dir: str | None = None) -> None:
    """Load review data and optional run output directory for the pipeline.

    Args:
        review_data_json: Full JSON string with keys ``title``, ``objective``,
            ``background``, ``selection_criteria``, and ``studies``.
        output_dir: Run output directory where ``search_metadata.json`` is written.
    """
    _run.review_data = json.loads(review_data_json)
    _run.output_dir = output_dir


def _require_output_dir() -> str:
    if not _run.output_dir:
        raise RuntimeError(
            "No output_dir configured. The runner must call "
            "load_review_data(..., output_dir=...) before the pipeline starts."
        )
    return _run.output_dir


# ---------------------------------------------------------------------------
# Tools for the Librarian agent
# ---------------------------------------------------------------------------

@tool
def search_studies(query: str) -> str:
    """
    Search for candidate studies relevant to a systematic review question.
    In this scaffolding version, it returns all candidate studies from the
    pre-loaded study database (simulating a real database search).

    The Boolean query is persisted to ``search_metadata.json`` in the run
    output directory.

    Args:
        query: The research question or search query.

    Returns:
        A formatted string listing all candidate studies with their index,
        title, and abstract (truncated).
    """
    if _run.review_data is None:
        return "ERROR: No review data loaded. The runner must call load_review_data() first."

    studies = _run.review_data.get("studies", [])
    try:
        update_search_strategy(
            _require_output_dir(),
            boolean_query=query,
            n_candidates=len(studies),
        )
    except RuntimeError as exc:
        return f"ERROR: {exc}"

    lines = [
        f"Search results for: {query}",
        f"Found {len(studies)} candidate studies.",
        f"Review: {_run.review_data.get('title', 'N/A')}",
        f"Selection criteria: {_run.review_data.get('selection_criteria', 'N/A')}",
        "",
    ]

    for i, study in enumerate(studies):
        title = study.get("title", "No title")
        abstract = study.get("abstract", "No abstract")
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
    if _run.review_data is None:
        return "ERROR: No review data loaded."

    return (
        f"=== REVIEW PROTOCOL ===\n"
        f"Title: {_run.review_data.get('title', 'N/A')}\n\n"
        f"Background:\n{_run.review_data.get('background', 'N/A')}\n\n"
        f"Objective:\n{_run.review_data.get('objective', 'N/A')}\n\n"
        f"Selection Criteria:\n{_run.review_data.get('selection_criteria', 'N/A')}\n"
    )


@tool
def record_search_description(description: str) -> str:
    """
    Record the narrative search strategy in ``search_metadata.json``.

    Call this after formulating the PICO-driven strategy and before
    ``search_studies()``.  Pass the strategy rationale only — do not
    include the Boolean query here (that is captured by ``search_studies``).

    Args:
        description: Narrative description of concepts, synonyms, and limits.

    Returns:
        Confirmation message.
    """
    try:
        update_search_strategy(_require_output_dir(), description=description)
    except RuntimeError as exc:
        return f"ERROR: {exc}"
    return "Search description saved to search_metadata.json."


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
    if _run.review_data is None:
        return "{}"
    return json.dumps(_run.review_data, ensure_ascii=False)
