"""
Prompt-formatting tools for Miner evidence extraction.

Package abstract text and the review objective into extraction tasks; the
miner agent fills JSON fields (population, intervention, outcomes, etc.).
"""

from smolagents import tool


@tool
def extract_evidence_from_abstract(
    study_title: str,
    study_abstract: str,
    review_objective: str,
    study_index: int,
) -> str:
    """
    Extract structured evidence from a study's abstract.
    Packages the study for the Miner agent to perform PICO extraction.

    Args:
        study_title: Title of the included study.
        study_abstract: Abstract text of the study.
        review_objective: The systematic review's research objective.
        study_index: Numeric index of this study.

    Returns:
        A formatted extraction task prompt for the agent.
    """
    return (
        f"=== EVIDENCE EXTRACTION TASK: Study {study_index} ===\n\n"
        f"RESEARCH QUESTION: {review_objective}\n\n"
        f"STUDY TITLE: {study_title}\n\n"
        f"STUDY ABSTRACT:\n{study_abstract}\n\n"
        f"INSTRUCTIONS: Extract structured evidence from this abstract.\n"
        f"Return a JSON object with these fields:\n"
        f"  - study_index: {study_index}\n"
        f"  - study_title: the study title\n"
        f"  - has_relevant_evidence: true/false\n"
        f"  - population: description of the study population\n"
        f"  - intervention: the intervention being studied\n"
        f"  - comparison: what it was compared against\n"
        f"  - outcomes: list of key outcome measures and results\n"
        f"  - study_design: type of study (RCT, cohort, etc.)\n"
        f"  - key_findings: list of main findings with data points\n"
    )


@tool
def batch_extract_evidence(included_studies_json: str, review_objective: str) -> str:
    """
    Prepare all included studies for batch evidence extraction.

    Args:
        included_studies_json: JSON string with list of included studies.
            Each study should have 'title', 'abstract', and 'study_index'.
        review_objective: The systematic review's research objective.

    Returns:
        A formatted batch extraction task for the Miner agent.
    """
    import json
    studies = json.loads(included_studies_json)

    lines = [
        f"=== BATCH EVIDENCE EXTRACTION ===",
        f"Research question: {review_objective}",
        f"Studies to extract from: {len(studies)}",
        "",
        "INSTRUCTIONS: For each study, extract PICO elements and key findings.",
        "Return a JSON list of extraction objects.",
        "",
    ]

    for study in studies:
        idx = study.get("study_index", "?")
        title = study.get("title", "No title")
        abstract = study.get("abstract", "No abstract")
        lines.append(f"--- Study {idx} ---")
        lines.append(f"Title: {title}")
        lines.append(f"Abstract: {abstract}")
        lines.append("")

    return "\n".join(lines)
