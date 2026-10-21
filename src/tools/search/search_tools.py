"""
Module-level study store and smolagents search/getter tools.

Runners call ``load_review_data`` once before the pipeline; the Librarian
may replace candidates via ``set_librarian_candidates``. External MCP search
returns the same ``{"meta", "rows"}`` shape as ``search_studies`` so agents
can treat local and remote results uniformly.

Getter tools at the bottom of this module feed batch and loop screening
orchestrators without exposing gold labels in chunk payloads.
"""

import json

from smolagents import tool

from mentor.tools.search.models import map_local_studies_to_result


# ---------------------------------------------------------------------------
# Module-level stores (populated by the runner before the pipeline)
# ---------------------------------------------------------------------------
# _review_data: review-level metadata ONLY (no studies) after load.
# The pipeline candidate list is published by the Librarian via
# set_librarian_candidates. Screening helpers may also fall back to the
# preloaded studies in ``_raw_review_json`` when no published set exists.
_review_data: dict | None = None

# _raw_review_json: the original JSON string (including studies) loaded
# from the dataset. Used by local search_studies() and as a fallback for
# screening getters when Librarian has not published candidates yet.
_raw_review_json: str | None = None


def load_review_data(review_data_json: str) -> None:
    """Load review data into the module-level stores.

    This is called once by the pipeline runner **before** the
    pipeline starts.

    It splits the incoming JSON into:
    - review-level metadata stored in ``_review_data`` (WITHOUT ``studies``)
    - the full original JSON string stored in ``_raw_review_json`` so that
      ``search_studies`` / screening helpers can reconstruct the study list
      on demand.

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


def _resolve_studies() -> list:
    """Return published candidates, else fall back to preloaded raw studies."""
    if _review_data is not None:
        studies = _review_data.get("studies")
        if isinstance(studies, list):
            return studies

    if _raw_review_json:
        try:
            full_data = json.loads(_raw_review_json)
        except json.JSONDecodeError:
            return []
        if isinstance(full_data, dict):
            studies = full_data.get("studies") or []
            return studies if isinstance(studies, list) else []
    return []


def _protocol_payload(studies: list) -> dict:
    """Build the shared screening/orchestrator payload shape."""
    if _review_data is None:
        raise ValueError("No review data loaded. The runner must call load_review_data() first.")
    return {
        "title": _review_data.get("title", ""),
        "objective": _review_data.get("objective", ""),
        "background": _review_data.get("background", ""),
        "selection_criteria": _review_data.get("selection_criteria", ""),
        "n_total": len(studies),
        "studies": studies,
    }


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
        return {
            "error": True,
            "message": "No review data loaded. The runner must call load_review_data() first.",
        }

    # Reconstruct the study list on demand from the raw JSON string,
    # without storing the parsed studies in module-level state.
    try:
        full_data = json.loads(_raw_review_json)
    except json.JSONDecodeError as e:  # noqa: BLE001
        return {
            "error": True,
            "message": f"Failed to parse review data JSON for local search: {e}",
        }

    if not isinstance(full_data, dict):
        return {
            "error": True,
            "message": "Review data JSON has unexpected structure.",
        }

    studies = full_data.get("studies", []) or []
    return map_local_studies_to_result(query=query, studies=studies).to_dict()


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
# Tools for the Orchestrator / screening runners
# ---------------------------------------------------------------------------

@tool
def get_candidates_json() -> str:
    """
    Return all candidate studies found by the librarian as a clean JSON
    string.  The orchestrator calls this after the librarian finishes to
    obtain a structured candidate list for the gatekeeper.

    The returned JSON has the same schema used by the screening and
    report tools: ``{"title": ..., "selection_criteria": ..., "n_total": N,
    "studies": [...]}``.

    Returns:
        A JSON string with the candidate studies and review metadata.
    """
    if _review_data is None:
        return "{}"
    studies = _resolve_studies()
    payload = dict(_review_data)
    payload["studies"] = studies
    payload["n_total"] = len(studies)
    return json.dumps(payload, ensure_ascii=False)


def _candidate_studies_chunk_payload(study_indices_json: str) -> str:
    """Shared implementation for single-study and chunk candidate getters."""
    try:
        raw_indices = json.loads(study_indices_json)
    except json.JSONDecodeError as exc:
        raise ValueError("study_indices_json must be a JSON array of study indices.") from exc
    if not isinstance(raw_indices, list) or not raw_indices:
        raise ValueError("study_indices_json must be a non-empty JSON array.")

    studies = _resolve_studies()
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

    payload = _protocol_payload(payload_studies)
    payload["n_total"] = len(studies)
    return json.dumps(payload, ensure_ascii=False)


