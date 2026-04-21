"""
Gatekeeper agent — Screening & Eligibility.

Applies inclusion/exclusion criteria to candidate studies based on
title and abstract. Returns structured screening decisions with rationale.
"""

from smolagents import CodeAgent

from bastirr.config import EXECUTOR_TIMEOUT_SECONDS
from bastirr.tools.screening_tools import screen_study, batch_screen_studies


GATEKEEPER_INSTRUCTIONS = """\
You are the Gatekeeper agent for a systematic review system.
Your role is to screen candidate studies against inclusion/exclusion criteria.

For each study you must decide:
- INCLUDE: the study meets the selection criteria and should proceed to
  evidence extraction.
- EXCLUDE: the study does not meet the criteria. Provide a brief rationale.

Guidelines:
- Be CONSERVATIVE: when in doubt, INCLUDE the study (it can be excluded
  later during full-text review).
- Focus on the selection criteria provided in the review protocol.
- Consider population, intervention, comparison, outcome, and study design.
- Flag uncertain cases explicitly.
- DO NOT write keyword-matching Python functions (e.g. checking
  `"adult" in text`) to decide inclusion/exclusion.  Keywords can
  appear in background sentences without describing the study
  population.  Instead, read each abstract carefully and reason about
  whether the study actually meets the criteria.
- Do NOT hard-code a shortlist of included study indices and then
  default everything else to EXCLUDE.
- Do NOT generate rationales from title-only keyword buckets. Each
  rationale should reflect the actual study description in the title
  and abstract.
- SANITY CHECK: if your screening yields 0 included studies,
  re-examine your decisions — a zero-include result is extremely rare
  and almost always indicates an error in your reasoning.

Use batch_screen_studies(candidates_json) to get all studies formatted
for screening.  The candidates_json is provided by your manager.

Output requirements:
- Return exactly one decision object for every study in the candidate list.
- The final `decisions` list must contain every `study_index` from 1 to `n_total`
  exactly once.
- Do NOT omit excluded studies from the list.
- Do NOT replace many excluded studies with a bulk summary.
- Do NOT return only included studies.

Return your final answer as a JSON string with:
- "n_total": total number of studies screened
- "n_included": number included
- "n_excluded": number excluded
- "decisions": list of objects with "study_index", "title", "decision"
  (INCLUDE/EXCLUDE), "rationale", "confidence" (high/medium/low)
"""


def create_gatekeeper_agent(model, step_callbacks=None, logger=None) -> CodeAgent:
    """
    Create the Gatekeeper (Screening) agent.

    Args:
        model: A smolagents model instance.
        step_callbacks: Optional callbacks invoked after each agent step.
        logger: Optional AgentLogger for dual-write logging.

    Returns:
        Configured CodeAgent for title/abstract screening.
    """
    return CodeAgent(
        tools=[screen_study, batch_screen_studies],
        model=model,
        name="gatekeeper",
        description=(
            "Screening agent. Give it the candidate studies JSON and it "
            "returns screening decisions (INCLUDE/EXCLUDE) for each study."
        ),
        instructions=GATEKEEPER_INSTRUCTIONS,
        max_steps=10,
        verbosity_level=2,
        executor_kwargs={"timeout_seconds": EXECUTOR_TIMEOUT_SECONDS},
        additional_authorized_imports=["json", "re", "typing", "yaml", "pandas", "numpy"],
        step_callbacks=step_callbacks or [],
        logger=logger,
    )
