"""
Critic agent — Synthesis & Quality Assessment.

Synthesizes extracted evidence into a coherent, citation-backed answer
and assesses methodological quality.
"""

from smolagents import CodeAgent

from bastirr.config import EXECUTOR_TIMEOUT_SECONDS
from bastirr.tools.synthesis_tools import synthesize_evidence, assess_evidence_quality


CRITIC_INSTRUCTIONS = """\
You are the Critic agent for a systematic review system.
Your role is to:
1. Assess the quality of included studies (bias, limitations).
2. Synthesize the extracted evidence into a coherent answer.

Quality assessment:
- Rate each study's quality (high/moderate/low).
- Identify potential sources of bias.
- Note limitations in study design or reporting.

Synthesis:
- Write an objective, data-driven synthesis citing studies by index [1], [2].
- Structure by outcome or intervention if there are multiple.
- Note conflicting findings and evidence gaps.
- Conclude with an assessment of overall evidence strength.

Steps:
1. Use assess_evidence_quality to evaluate study quality.
2. Use synthesize_evidence to create the final synthesis.

Return your final answer as a JSON string with:
- "quality_assessments": list of per-study quality ratings
- "synthesis": the narrative synthesis text with citations
- "evidence_strength": overall assessment (strong/moderate/weak/insufficient)
- "limitations": key limitations across studies
"""


def create_critic_agent(model, logger=None) -> CodeAgent:
    """
    Create the Critic (Synthesis & Quality) agent.

    Args:
        model: A smolagents model instance.
        logger: Optional AgentLogger for dual-write logging.

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
        instructions=CRITIC_INSTRUCTIONS,
        max_steps=5,
        verbosity_level=2,
        executor_kwargs={"timeout_seconds": EXECUTOR_TIMEOUT_SECONDS},
        additional_authorized_imports=["json", "re"],
        logger=logger,
    )
