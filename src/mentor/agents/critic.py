"""
Critic agent — evidence synthesis and quality assessment.

Consumes miner output and produces a narrative answer with study-index
citations plus a separate quality/bias pass over included studies.
"""

from smolagents import CodeAgent

from mentor.config import EXECUTOR_TIMEOUT_SECONDS
from mentor.agents.prompts import load_prompt
from mentor.tools.synthesis_tools import assess_evidence_quality, synthesize_evidence


def create_critic_agent(
    model,
    step_callbacks=None,
    logger=None,
    instructions: str | None = None,
) -> CodeAgent:
    """
    Create the Critic (Synthesis & Quality) agent.

    Args:
        model: A smolagents model instance.
        step_callbacks: Optional callbacks invoked after each agent step.
        logger: Optional AgentLogger for dual-write logging.
        instructions: Optional system prompt override.

    Returns:
        Configured CodeAgent for synthesis and quality assessment.
    """
    return CodeAgent(
        tools=[synthesize_evidence, assess_evidence_quality],
        model=model,
        name="critic",
        description=(
            "Synthesis and quality assessment agent. Give it extracted "
            "evidence (as JSON) and the review objective, and it produces "
            "a quality assessment and narrative synthesis with citations."
        ),
        instructions=instructions or load_prompt("critic"),
        max_steps=5,
        verbosity_level=2,
        executor_kwargs={"timeout_seconds": EXECUTOR_TIMEOUT_SECONDS},
        additional_authorized_imports=["json", "re", "yaml", "pandas", "numpy"],
        step_callbacks=step_callbacks or [],
        logger=logger,
    )
