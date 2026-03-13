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

from bastirr.models.search import SearchMeta, SearchResult, StudyRow


# ---------------------------------------------------------------------------
# Module-level stores (populated by the runner before the pipeline)
# ---------------------------------------------------------------------------
# _review_data: review-level metadata ONLY (no studies). The studies list
# used by the pipeline is always written by the Librarian via
# set_librarian_candidates.
_review_data: dict | None = None

# _raw_review_json: the original JSON string (including studies) loaded
# from the dataset. This is only used inside search_studies() to
# reconstruct the temporary study list for display or JSON output; the
# parsed studies are never stored in module-level state.
_raw_review_json: str | None = None


def load_review_data(review_data_json: str) -> None:
    """Load review data into the module-level stores.

    This is called once by ``run_demo.py`` (or any runner) **before** the
    pipeline starts.

    It splits the incoming JSON into:
    - review-level metadata stored in ``_review_data`` (WITHOUT ``studies``)
    - the full original JSON string stored in ``_raw_review_json`` so that
      ``search_studies`` can reconstruct the study list on demand.

    Args:
        review_data_json: Full JSON string with keys ``title``, ``objective``,
            ``background``, ``selection_criteria``, and ``studies``.
    """
    global _review_data, _raw_review_json
    _raw_review_json = review_data_json

    data = json.loads(review_data_json)
    if isinstance(data, dict):
        # Keep all non-study fields as review-level metadata.
        _review_data = {k: v for k, v in data.items() if k != "studies"}
    else:
        # Fallback: store as-is; search_studies may still parse _raw_review_json.
        _review_data = data


# ---------------------------------------------------------------------------
# Tools for the Librarian agent
# ---------------------------------------------------------------------------

@tool
def search_studies(query: str) -> dict:
    """
    Search for candidate studies relevant to a systematic review question.
    In this scaffolding version, it returns all candidate studies from the
    pre-loaded study database (simulating a real database search) as a JSON
    string with the same ``{"meta": ..., "rows": [...]}`` format used by
    the external BIP MCP ``paper_search`` tool.

    Args:
        query: The research question or search query.

    Returns:
        A Python dict with the normalized search result:

            {
              "meta": {
                "source": "local",
                "query": <query>,
                "total_count": <number_of_studies>,
                "page": 1,
                "page_size": <number_of_studies>
              },
              "rows": [
                {
                  "study_index": <1-based_index>,
                  "title": <title>,
                  "abstract": <abstract>
                },
                ...
              ]
            }
    """
    if _review_data is None or _raw_review_json is None:
        return json.dumps(
            {
                "error": True,
                "message": "No review data loaded. The runner must call load_review_data() first.",
            },
            ensure_ascii=False,
        )

    # Reconstruct the study list on demand from the raw JSON string,
    # without storing the parsed studies in module-level state.
    try:
        full_data = json.loads(_raw_review_json)
    except json.JSONDecodeError as e:  # noqa: BLE001
        return json.dumps(
            {
                "error": True,
                "message": f"Failed to parse review data JSON for local search: {e}",
            },
            ensure_ascii=False,
        )

    if not isinstance(full_data, dict):
        return json.dumps(
            {
                "error": True,
                "message": "Review data JSON has unexpected structure.",
            },
            ensure_ascii=False,
        )

    studies = full_data.get("studies", []) or []
    rows: list[StudyRow] = []
    for i, study in enumerate(studies):
        title = study.get("title", "No title") if isinstance(study, dict) else "No title"
        abstract = (
            study.get("abstract", "No abstract") if isinstance(study, dict) else "No abstract"
        )
        rows.append(StudyRow(study_index=i + 1, title=title, abstract=abstract))

    meta = SearchMeta(
        source="local",
        query=query,
        total_count=len(rows),
        page=1,
        page_size=len(rows),
    )
    result = SearchResult(meta=meta, rows=rows)
    return result.to_dict()


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


@tool
def set_librarian_candidates(studies: list) -> str:
    """
    Publish the Librarian's final candidate set for the rest of the pipeline.

    Call once with the list of study dicts (each with study_index, title,
    abstract). Replaces only the ``studies`` field in shared review data;
    review-level metadata is preserved.

    Args:
        studies: List of study dicts.

    Returns:
        A short confirmation message.
    """
    global _review_data

    if not isinstance(studies, list):
        return "ERROR: studies must be a list."

    # Merge studies into existing review dict (preserves title, objective, etc.).
    if _review_data is None:
        _review_data = {}
    _review_data["studies"] = studies

    return f"OK: stored {len(studies)} candidate studies for the pipeline."


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

