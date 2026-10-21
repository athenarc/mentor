"""
Prompt-formatting tools for Gatekeeper screening.

These tools do not call an LLM themselves; they assemble criteria + study
text so the gatekeeper agent can reason and emit structured INCLUDE/EXCLUDE
JSON in its final answer.
"""

from smolagents import tool


@tool
def screen_studies(candidates_json: str) -> str:
    """
    Prepare candidate studies for screening (one study or many).

    Returns a formatted list of studies with the selection criteria, ready
    for the Gatekeeper agent to make decisions on each. Pass a single study
    in ``studies`` for one-at-a-time screening.

    Args:
        candidates_json: JSON string with candidate studies. Must contain
            keys 'studies' (list), 'title', and 'selection_criteria'.

    Returns:
        A formatted string with all studies and criteria, requesting
        a structured screening decision for each.
    """
    import json
    review = json.loads(candidates_json)
    criteria = review.get("selection_criteria", "N/A")
    studies = review.get("studies", [])

    lines = [
        "=== SCREENING TASK ===",
        f"Review: {review.get('title', 'N/A')}",
        f"Total studies to screen: {len(studies)}",
        "",
        "SELECTION CRITERIA:",
        f"{criteria}",
        "",
        "INSTRUCTIONS: For each study below, decide INCLUDE or EXCLUDE.",
        "Return exactly one decision object per study; do not omit excluded studies, "
        "do not summarize exclusions in bulk, and do not return only included studies.",
        "Return a JSON list with objects having keys: "
        "'study_index', 'decision' (INCLUDE/EXCLUDE), 'rationale'.",
        "",
    ]

    for i, study in enumerate(studies):
        study_index = study.get("study_index", i + 1)
        title = study.get("title", "No title")
        abstract = study.get("abstract", "No abstract")
        lines.append(f"--- Study {study_index} ---")
        lines.append(f"Title: {title}")
        lines.append(f"Abstract: {abstract}")
        lines.append("")

    return "\n".join(lines)
