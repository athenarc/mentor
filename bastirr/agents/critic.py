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
- Write an objective, data-driven narrative synthesis citing studies
  by index [1], [2].
- Structure by outcome or intervention if there are multiple.
- Note conflicting findings and evidence gaps.
- Conclude with an assessment of overall evidence strength.

Steps:
1. Use assess_evidence_quality to evaluate study quality.
2. Use synthesize_evidence to create the final synthesis.

CODE RULES:
- NEVER use locals(), globals(), exec(), or eval() — they are blocked
  by the execution sandbox. Use try/except or explicit variable checks
  instead.
- Use json.loads() and json.dumps() for all JSON operations.

═══════════════════════════════════════════════════════════════════════
OUTPUT SCHEMA — you MUST return final_answer() as a JSON string
with EXACTLY this structure and EXACTLY these key names.
Do NOT rename, nest, or wrap these keys.
═══════════════════════════════════════════════════════════════════════

{
  "quality_assessments": [
    {
      "study_index": 1,
      "citation": "Author Year",
      "quality_rating": "high" | "moderate" | "low",
      "strengths": ["strength 1", ...],
      "limitations": ["limitation 1", ...],
      "risk_of_bias": "low" | "unclear" | "high",
      "risk_of_bias_concerns": ["concern 1", ...],
      "applicability": "direct" | "indirect"
    }
  ],
  "synthesis": "Narrative text citing studies by [1], [2], ...",
  "evidence_strength": "strong" | "moderate" | "weak" | "insufficient",
  "limitations": ["limitation 1", "limitation 2", ...]
}

Rules:
- "synthesis" MUST contain your own narrative text — NOT the raw
  output of the synthesize_evidence() tool scaffold.
  Remove any "=== EVIDENCE SYNTHESIS TASK ===" blocks or tool prompts.
- "quality_assessments" MUST be a flat list (not nested in a wrapper).
- Use the EXACT key names shown above.
- Your final_answer MUST include the JSON object above.  You may also
  include the "### 1. Task outcome" / "### 2. Task outcome" /
  "### 3. Additional context" narrative sections for your manager,
  but keep them OUTSIDE the JSON.  Never embed those section headers
  inside any JSON field value (especially "synthesis").
"""


def create_critic_agent(model, step_callbacks=None, logger=None) -> CodeAgent:
    """
    Create the Critic (Synthesis & Quality) agent.

    Args:
        model: A smolagents model instance.
        step_callbacks: Optional callbacks invoked after each agent step.
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
        max_steps=10,
        verbosity_level=2,
        executor_kwargs={"timeout_seconds": EXECUTOR_TIMEOUT_SECONDS},
        additional_authorized_imports=["json", "re", "yaml", "pandas", "numpy"],
        step_callbacks=step_callbacks or [],
        logger=logger,
    )
