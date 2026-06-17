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


@tool
def get_candidate_study_json(study_index: int) -> str:
    """
    Return exactly one candidate study for looped screening.

    The payload intentionally excludes gold labels and does not include the
    full candidate set.  It contains protocol context plus the requested
    study's title and abstract so the Gatekeeper can classify that study in
    isolation.

    Args:
        study_index: One-based study index to retrieve.

    Returns:
        A JSON string with review protocol fields, ``n_total``, and one
        ``study`` object.
    """
    if _review_data is None:
        raise ValueError("No review data loaded. The runner must call load_review_data() first.")

    studies = _review_data.get("studies", [])
    try:
        index = int(study_index)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Invalid study_index: {study_index!r}") from exc

    if index < 1 or index > len(studies):
        raise ValueError(
            f"study_index {index} is outside the available range 1..{len(studies)}"
        )

    study = studies[index - 1]
    payload = {
        "title": _review_data.get("title", ""),
        "objective": _review_data.get("objective", ""),
        "background": _review_data.get("background", ""),
        "selection_criteria": _review_data.get("selection_criteria", ""),
        "n_total": len(studies),
        "study": {
            "study_index": index,
            "title": study.get("title", ""),
            "abstract": study.get("abstract", ""),
        },
    }
    return json.dumps(payload, ensure_ascii=False)


@tool
def get_candidate_studies_chunk_json(study_indices_json: str) -> str:
    """
    Return a label-free chunk of candidate studies for mini-batch screening.

    The payload intentionally excludes gold labels and does not include the
    full candidate set.  It contains protocol context, the full review study
    count, and only the requested studies with their original one-based
    ``study_index`` values.

    Args:
        study_indices_json: JSON array string of one-based study indices.

    Returns:
        A JSON string with review protocol fields, ``n_total``,
        ``chunk_study_indices``, and a ``studies`` list.
    """
    if _review_data is None:
        raise ValueError("No review data loaded. The runner must call load_review_data() first.")

    try:
        raw_indices = json.loads(study_indices_json)
    except json.JSONDecodeError as exc:
        raise ValueError("study_indices_json must be a JSON array of study indices.") from exc
    if not isinstance(raw_indices, list) or not raw_indices:
        raise ValueError("study_indices_json must be a non-empty JSON array.")

    studies = _review_data.get("studies", [])
    indices: list[int] = []
    for raw_index in raw_indices:
        try:
            index = int(raw_index)
        except (TypeError, ValueError) as exc:
            raise ValueError(f"Invalid study index in chunk: {raw_index!r}") from exc
        if index < 1 or index > len(studies):
            raise ValueError(
                f"study_index {index} is outside the available range 1..{len(studies)}"
            )
        if index in indices:
            raise ValueError(f"Duplicate study index in chunk: {index}")
        indices.append(index)

    payload_studies = []
    for index in indices:
        study = studies[index - 1]
        payload_studies.append({
            "study_index": index,
            "title": study.get("title", ""),
            "abstract": study.get("abstract", ""),
        })

    payload = {
        "title": _review_data.get("title", ""),
        "objective": _review_data.get("objective", ""),
        "background": _review_data.get("background", ""),
        "selection_criteria": _review_data.get("selection_criteria", ""),
        "n_total": len(studies),
        "chunk_study_indices": indices,
        "studies": payload_studies,
    }
    return json.dumps(payload, ensure_ascii=False)
