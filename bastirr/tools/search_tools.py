"""
Search & retrieval tools for the Librarian agent.

In the full Bastirr system, the Librarian would query PubMed, OpenAIRE, etc.
For this scaffolding, it retrieves candidate studies from the pre-loaded
Cochrane dataset — simulating a "search" by returning title + abstract records.
"""

from smolagents import tool


@tool
def search_studies(query: str, review_data_json: str) -> str:
    """
    Search for candidate studies relevant to a systematic review question.
    In this scaffolding version, it returns all candidate studies from the
    pre-loaded Cochrane dataset (simulating a database search).

    Args:
        query: The research question or search query.
        review_data_json: JSON string containing the review data with studies.
            Must have keys: 'title', 'objective', 'selection_criteria', 'studies'.
            Each study has 'title' and 'abstract'.

    Returns:
        A formatted string listing all candidate studies with their index,
        title, and abstract (truncated).
    """
    import json
    review = json.loads(review_data_json)
    studies = review.get("studies", [])

    lines = [
        f"Search results for: {query}",
        f"Found {len(studies)} candidate studies.",
        f"Review: {review.get('title', 'N/A')}",
        f"Selection criteria: {review.get('selection_criteria', 'N/A')}",
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
def get_review_protocol(review_data_json: str) -> str:
    """
    Extract the review protocol (objective, background, selection criteria)
    from the review data. The Librarian uses this to formulate search strategies.

    Args:
        review_data_json: JSON string containing the review data.

    Returns:
        A formatted string with the review protocol details.
    """
    import json
    review = json.loads(review_data_json)

    return (
        f"=== REVIEW PROTOCOL ===\n"
        f"Title: {review.get('title', 'N/A')}\n\n"
        f"Background:\n{review.get('background', 'N/A')}\n\n"
        f"Objective:\n{review.get('objective', 'N/A')}\n\n"
        f"Selection Criteria:\n{review.get('selection_criteria', 'N/A')}\n"
    )
