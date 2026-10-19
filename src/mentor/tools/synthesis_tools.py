"""
Prompt-formatting tools for Critic synthesis and quality review.

``synthesize_evidence`` prepares a narrative task; ``assess_evidence_quality``
prepares a separate bias/quality pass over the same extracted JSON.
"""

from smolagents import tool


@tool
def synthesize_evidence(extracted_evidence_json: str, review_objective: str) -> str:
    """
    Prepare extracted evidence for synthesis into a coherent answer.
    Packages all extracted evidence for the Critic agent to synthesize.

    Args:
        extracted_evidence_json: JSON string containing all extracted evidence.
            A list of evidence objects from the Miner.
        review_objective: The systematic review's research objective.

    Returns:
        A formatted synthesis task prompt for the agent.
    """
    return (
        f"=== EVIDENCE SYNTHESIS TASK ===\n\n"
        f"RESEARCH QUESTION: {review_objective}\n\n"
        f"EXTRACTED EVIDENCE:\n{extracted_evidence_json}\n\n"
        f"INSTRUCTIONS: Synthesize the extracted evidence into a coherent, "
        f"citation-backed answer to the research question.\n"
        f"Guidelines:\n"
        f"  - Cite studies by their study_index: [1], [2], etc.\n"
        f"  - Be objective and data-driven.\n"
        f"  - Note limitations, conflicting findings, and evidence gaps.\n"
        f"  - Structure by outcome or intervention if multiple exist.\n"
        f"  - End with a brief conclusion on evidence strength.\n"
    )


@tool
def assess_evidence_quality(extracted_evidence_json: str) -> str:
    """
    Prepare extracted evidence for quality/bias assessment.
    The Critic evaluates methodological quality of included studies.

    Args:
        extracted_evidence_json: JSON string containing all extracted evidence.

    Returns:
        A formatted quality assessment task for the agent.
    """
    return (
        f"=== QUALITY ASSESSMENT TASK ===\n\n"
        f"EXTRACTED EVIDENCE:\n{extracted_evidence_json}\n\n"
        f"INSTRUCTIONS: Assess the quality of each study based on the "
        f"information available in the extracted evidence.\n"
        f"For each study, evaluate:\n"
        f"  - Study design strength (RCT > cohort > case-control > case series)\n"
        f"  - Sample size adequacy\n"
        f"  - Potential sources of bias based on description\n"
        f"  - Applicability of findings to the review question\n\n"
        f"Return a JSON list with objects having keys: "
        f"'study_index', 'quality_rating' (high/moderate/low), "
        f"'strengths', 'limitations', 'risk_of_bias_concerns'.\n"
    )
