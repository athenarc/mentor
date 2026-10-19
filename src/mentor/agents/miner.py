"""
Miner agent — structured evidence extraction from abstracts.

The Cochrane dataset provides abstracts only (no full text), so extraction
is limited to PICO-style fields and key findings surfaced in the abstract text.
"""

from smolagents import CodeAgent

from mentor.settings import EXECUTOR_TIMEOUT_SECONDS
from mentor.agents.prompts import load_prompt
from mentor.tools.extraction_tools import (
    batch_extract_evidence,
    extract_evidence_from_abstract,
)


def create_miner_agent(
    model,
    step_callbacks=None,
    logger=None,
    instructions: str | None = None,
) -> CodeAgent:
    """
    Create the Miner (Evidence Extraction) agent.

    Args:
        model: A smolagents model instance.
        step_callbacks: Optional callbacks invoked after each agent step.
        logger: Optional AgentLogger for dual-write logging.
        instructions: Optional system prompt override.

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
        instructions=instructions or load_prompt("miner"),
        max_steps=5,
        verbosity_level=2,
        executor_kwargs={"timeout_seconds": EXECUTOR_TIMEOUT_SECONDS},
        additional_authorized_imports=["json", "re", "typing", "yaml", "pandas", "numpy"],
        step_callbacks=step_callbacks or [],
        logger=logger,
    )
