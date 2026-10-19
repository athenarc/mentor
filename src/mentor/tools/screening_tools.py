"""
Prompt-formatting tools for Gatekeeper screening.

These tools do not call an LLM themselves; they assemble criteria + study
text so the gatekeeper agent can reason and emit structured INCLUDE/EXCLUDE
JSON in its final answer.
"""

from smolagents import tool


@tool
def screen_study(
    study_title: str,
    study_abstract: str,
    selection_criteria: str,
    study_index: int,
) -> str:
    """
    Screen a single study against the review's selection criteria.
    Returns a structured screening decision for one study.

    This tool packages the study information for the Gatekeeper agent
    to make an inclusion/exclusion decision. The agent itself applies
    the criteria using LLM reasoning.

    Args:
        study_title: Title of the candidate study.
        study_abstract: Abstract text of the candidate study.
        selection_criteria: The review's inclusion/exclusion criteria.
        study_index: Numeric index of this study in the candidate list.

    Returns:
        A formatted string containing the study details and criteria
        for the agent to evaluate.
    """
    return (
        f"=== SCREENING TASK: Study {study_index} ===\n\n"
        f"SELECTION CRITERIA:\n{selection_criteria}\n\n"
        f"STUDY TITLE:\n{study_title}\n\n"
        f"STUDY ABSTRACT:\n{study_abstract}\n\n"
        f"INSTRUCTIONS: Based on the selection criteria above, decide whether "
        f"this study should be INCLUDED or EXCLUDED. Provide a brief rationale "
        f"tied to specific criteria.\n"
    )


@tool
def batch_screen_studies(candidates_json: str) -> str:
    """
    Prepare all candidate studies for batch screening.
    Returns a formatted list of all studies with the selection criteria,
    ready for the Gatekeeper agent to make decisions on each.

    Args:
        candidates_json: JSON string with candidate studies.  Must contain
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
        f"=== BATCH SCREENING TASK ===",
        f"Review: {review.get('title', 'N/A')}",
        f"Total studies to screen: {len(studies)}",
        f"",
        f"SELECTION CRITERIA:",
        f"{criteria}",
        f"",
        f"INSTRUCTIONS: For each study below, decide INCLUDE or EXCLUDE.",
        f"Return exactly one decision object per study; do not omit excluded studies, "
        f"do not summarize exclusions in bulk, and do not return only included studies.",
        f"Return a JSON list with objects having keys: "
        f"'study_index', 'decision' (INCLUDE/EXCLUDE), 'rationale'.",
        f"",
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
