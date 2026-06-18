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


SINGLE_STUDY_GATEKEEPER_INSTRUCTIONS = """\
You are the Gatekeeper agent for a systematic review screening benchmark.
Your role is to classify exactly one candidate study against the review
protocol's title/abstract screening criteria.

For the single study provided, decide:
- INCLUDE: the study meets the selection criteria or is uncertain enough to
  proceed to later review.
- EXCLUDE: the study clearly does not meet the criteria.

Guidelines:
- Be CONSERVATIVE: when in doubt, INCLUDE the study.
- Consider population, intervention, comparison, outcome, and study design.
- Do NOT use keyword-only heuristics. Read the title and abstract carefully.
- The rationale must be specific to this study and tied to the protocol.
- Do NOT reuse boilerplate rationales.

Use screen_study(study_title, study_abstract, selection_criteria, study_index)
to format the screening task before making your decision.

Return your final answer as a JSON string with:
- "n_total": 1
- "n_included": 0 or 1
- "n_excluded": 0 or 1
- "decisions": a one-item list with "study_index", "title", "decision"
  (INCLUDE/EXCLUDE), "rationale", and "confidence" (high/medium/low)
"""


CHUNK_GATEKEEPER_INSTRUCTIONS = """\
You are the Gatekeeper agent for a systematic review screening benchmark.
Your role is to classify a bounded mini-batch of candidate studies against
the review protocol's title/abstract screening criteria.

For each study in the mini-batch, decide:
- INCLUDE: the study meets the selection criteria or is uncertain enough to
  proceed to later review.
- EXCLUDE: the study clearly does not meet the criteria.

Guidelines:
- Be CONSERVATIVE: when in doubt, INCLUDE the study.
- Consider population, intervention, comparison, outcome, and study design.
- Do NOT use keyword-only heuristics. Read each title and abstract carefully.
- Write a distinct rationale for every study, tied to that study and protocol.
- Do NOT cluster studies into bulk rationale categories.
- Do NOT omit excluded studies.

Use batch_screen_studies(candidates_json) to format the mini-batch before
making decisions. The candidates_json contains only this chunk, not the full
review.

Output requirements:
- Return exactly one decision object for every study in the chunk.
- Preserve the original study_index values from the chunk payload.
- Do NOT renumber chunk studies from 1 unless those are their original indices.
- Do NOT include decisions for studies outside the chunk.

Return your final answer as a JSON string with:
- "n_total": total number of studies screened in this chunk
- "n_included": number included in this chunk
- "n_excluded": number excluded in this chunk
- "decisions": list of objects with "study_index", "title", "decision"
  (INCLUDE/EXCLUDE), "rationale", and "confidence" (high/medium/low)
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
        max_steps=20,
        verbosity_level=2,
        executor_kwargs={"timeout_seconds": EXECUTOR_TIMEOUT_SECONDS},
        additional_authorized_imports=["json", "re", "typing", "yaml", "pandas", "numpy", "pickle", "sys"],
        step_callbacks=step_callbacks or [],
        logger=logger,
    )


def create_single_study_gatekeeper_agent(model, step_callbacks=None, logger=None) -> CodeAgent:
    """
    Create a Gatekeeper agent constrained to one study per managed call.

    The loop benchmark uses this factory so each Gatekeeper task is
    self-contained and cannot reason over the whole review's candidate set.
    """
    return CodeAgent(
        tools=[screen_study],
        model=model,
        name="gatekeeper",
        description=(
            "Single-study screening agent. Give it one study plus the review "
            "protocol and it returns exactly one INCLUDE/EXCLUDE decision."
        ),
        instructions=SINGLE_STUDY_GATEKEEPER_INSTRUCTIONS,
        max_steps=20,
        verbosity_level=2,
        executor_kwargs={"timeout_seconds": EXECUTOR_TIMEOUT_SECONDS},
        additional_authorized_imports=["json", "re", "typing", "yaml", "pandas", "numpy", "pickle", "sys"],
        step_callbacks=step_callbacks or [],
        logger=logger,
    )


def create_chunk_gatekeeper_agent(model, step_callbacks=None, logger=None) -> CodeAgent:
    """
    Create a Gatekeeper agent constrained to one bounded study chunk per call.
    """
    return CodeAgent(
        tools=[batch_screen_studies],
        model=model,
        name="gatekeeper",
        description=(
            "Mini-batch screening agent. Give it one bounded study chunk plus "
            "the review protocol and it returns one decision per chunk study."
        ),
        instructions=CHUNK_GATEKEEPER_INSTRUCTIONS,
        max_steps=20,
        verbosity_level=2,
        executor_kwargs={"timeout_seconds": EXECUTOR_TIMEOUT_SECONDS},
        additional_authorized_imports=["json", "re", "typing", "yaml", "pandas", "numpy", "pickle", "sys"],
        step_callbacks=step_callbacks or [],
        logger=logger,
    )
