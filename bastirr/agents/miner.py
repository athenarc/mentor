"""
Miner agent — Evidence Extraction.

Extracts structured evidence (PICO elements, key findings) from
included studies' abstracts.
"""

from smolagents import CodeAgent

from bastirr.config import EXECUTOR_TIMEOUT_SECONDS
from bastirr.tools.extraction_tools import (
    extract_evidence_from_abstract,
    batch_extract_evidence,
)


MINER_INSTRUCTIONS = """\
You are the Miner agent for a systematic review system.
Your role is to extract structured evidence from included studies.

For each included study, extract:
- Population: who was studied
- Intervention: what was done
- Comparison: what it was compared to
- Outcomes: what was measured and the results
- Study design: RCT, cohort, etc.
- Key findings: specific data points, effect sizes, p-values

Use batch_extract_evidence to process all included studies at once.

Return your final answer as a JSON string with:
- "n_studies_processed": number of studies processed
- "extractions": list of evidence extraction objects, each with
  "study_index", "study_title", "has_relevant_evidence", "population",
  "intervention", "comparison", "outcomes" (list), "study_design",
  "key_findings" (list)
"""


def create_miner_agent(model) -> CodeAgent:
    """
    Create the Miner (Evidence Extraction) agent.

    Args:
        model: A smolagents model instance.

    Returns:
        Configured CodeAgent for evidence extraction.
    """
    return CodeAgent(
        tools=[extract_evidence_from_abstract, batch_extract_evidence],
        model=model,
        name="miner",
        description=(
            "Evidence extraction agent. Give it a list of included studies "
            "(as JSON with title, abstract, study_index) and the review "
            "objective, and it extracts structured PICO evidence from each."
        ),
        instructions=MINER_INSTRUCTIONS,
        max_steps=5,
        verbosity_level=1,
        executor_kwargs={"timeout_seconds": EXECUTOR_TIMEOUT_SECONDS},
    )
