"""
Thin orchestrator for the Gatekeeper screening benchmark.

This orchestrator mirrors the live handoff boundary:
- it receives protocol-only task text
- retrieves the loaded candidates through get_candidates_json()
- delegates screening to the real Gatekeeper
- persists screening decisions to evidence.json
"""

from smolagents import CodeAgent

from bastirr.agents.gatekeeper import create_gatekeeper_agent
from bastirr.agents.wrappers import GATEKEEPER_BATCH_TASK, wrap_gatekeeper
from bastirr.errors import with_error_abort_callback
from bastirr.config import EXECUTOR_TIMEOUT_SECONDS
from bastirr.tools.screening_benchmark_tools import (
    format_screening_summary,
    save_screening_evidence_json,
)
from bastirr.tools.search_tools import get_candidates_json


SCREENING_ORCHESTRATOR_INSTRUCTIONS = """\
You are the Orchestrator agent for a Gatekeeper screening benchmark.
You coordinate only the title/abstract screening phase.

You receive ONLY the review protocol text. You do NOT receive raw studies
in the task itself. Retrieve the candidates via get_candidates_json()
after reading the protocol.

You have one managed agent:
1. **gatekeeper** — screens studies for inclusion/exclusion

You have three utility tools:
- **get_candidates_json** — returns the preloaded candidate studies as JSON
- **save_screening_evidence_json** — saves screening outputs to evidence.json
- **format_screening_summary** — returns a short Markdown summary

CRITICAL RULES
1. ONE AGENT CALL PER CODE BLOCK.
2. ALWAYS USE YOUR TOOLS — do NOT write custom parsers for the gatekeeper output.
3. Do NOT add stricter screening instructions than the protocol already provides.
4. Do NOT pre-judge individual studies.
5. The Gatekeeper output must contain exactly one decision object per study.
6. If the Gatekeeper returns an incomplete decision list, rerun it before saving.
7. Do NOT reconstruct screening decisions yourself in orchestrator code.
8. Do NOT hard-code include/exclude indices, titles, or study-specific verdicts.
9. Do NOT use keyword-matching heuristics to generate screening decisions or rationales.
10. If the Gatekeeper response cannot be saved as a complete per-study decision set,
    fail closed and rerun the Gatekeeper; do not create a manager-side fallback list.
11. Call gatekeeper(task="", additional_args={"screening_payload": candidates_json}).
    The task argument is ignored by the gatekeeper wrapper; pass study data ONLY via
    additional_args. Never paste study JSON into task=.
12. On Gatekeeper failure (including context overflow), let the error surface;
    do not invent recovery strategies.

WORKFLOW
Code block 1:
  - Read the review title and selection criteria from the task.
  - Call get_candidates_json().
  - Print how many candidates were loaded.

Code block 2:
  - Call gatekeeper(task="", additional_args={"screening_payload": ...}).
  - Ensure the gatekeeper response contains one decision per study; do not accept
    outputs that summarize excluded studies without individual decisions.
  - Call save_screening_evidence_json(screening_response=gatekeeper_response, output_dir=output_dir, expected_n_studies=expected_n_studies).
  - Call format_screening_summary(review_title=review_title, screening_response=gatekeeper_response).
  - Return the formatted summary with final_answer().
"""


def create_screening_orchestrator_agent(
    orchestrator_model,
    gatekeeper_model,
    step_callbacks=None,
    logger=None,
    max_steps: int = 20,
) -> CodeAgent:
    """
    Create the thin screening orchestrator used by the benchmark harness.

    Args:
        orchestrator_model: Model instance for the thin orchestrator.
        gatekeeper_model: Model instance for the Gatekeeper agent.
        step_callbacks: Optional smolagents step callbacks.
        logger: Optional shared AgentLogger instance.
        max_steps: Maximum smolagents steps for the thin Orchestrator.

    Returns:
        Configured CodeAgent that manages only candidate retrieval and screening.
    """
    step_callbacks = with_error_abort_callback(step_callbacks)
    gatekeeper = wrap_gatekeeper(
        create_gatekeeper_agent(
            gatekeeper_model,
            step_callbacks=step_callbacks,
            logger=logger,
        ),
        fixed_task=GATEKEEPER_BATCH_TASK,
    )

    return CodeAgent(
        tools=[
            get_candidates_json,
            save_screening_evidence_json,
            format_screening_summary,
        ],
        model=orchestrator_model,
        managed_agents=[gatekeeper],
        name="orchestrator",
        instructions=SCREENING_ORCHESTRATOR_INSTRUCTIONS,
        max_steps=max_steps,
        verbosity_level=2,
        executor_kwargs={"timeout_seconds": EXECUTOR_TIMEOUT_SECONDS},
        step_callbacks=step_callbacks,
        additional_authorized_imports=["json", "re", "typing", "yaml", "pandas", "numpy", "sys", "pickle"],
        logger=logger,
    )
