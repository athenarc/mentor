"""
Looped Orchestrator for one-study-at-a-time Gatekeeper benchmarks.

This agent keeps the benchmark separate from the existing batch screening
Orchestrator.  It retrieves one candidate study by index, delegates that
single study to Gatekeeper, and appends the result immediately.
"""

from smolagents import CodeAgent

from bastirr.agents.gatekeeper import (
    create_chunk_gatekeeper_agent,
    create_single_study_gatekeeper_agent,
)
from bastirr.agents.wrappers import (
    GATEKEEPER_CHUNK_TASK,
    GATEKEEPER_SINGLE_STUDY_TASK,
    wrap_gatekeeper,
)
from bastirr.errors import with_error_abort_callback
from bastirr.config import EXECUTOR_TIMEOUT_SECONDS
from bastirr.tools.screening_benchmark_tools import (
    append_screening_chunk_decisions_json,
    append_screening_decision_json,
    format_screening_progress_summary,
)
from bastirr.tools.search_tools import (
    get_candidate_studies_chunk_json,
    get_candidate_study_json,
)


SCREENING_LOOP_ORCHESTRATOR_INSTRUCTIONS = """\
You are the Orchestrator agent for a looped Gatekeeper screening benchmark.
You coordinate only title/abstract screening, one study at a time.

You receive protocol context and a list of study indices to process. You do
NOT receive raw studies in the task itself. Retrieve each study only through
get_candidate_study_json(study_index), which returns exactly one label-free
candidate study.

You have one managed agent:
1. **gatekeeper** — screens exactly one study for inclusion/exclusion

You have three utility tools:
- **get_candidate_study_json** — returns one label-free candidate study
- **append_screening_decision_json** — appends one parsed decision to evidence.json
- **format_screening_progress_summary** — returns a short Markdown summary

CRITICAL RULES
1. Never call get_candidates_json or any all-candidate retrieval helper.
2. Never place raw study data in your final answer.
3. Process only the study indices listed in the task.
4. For each study index, call get_candidate_study_json(index), then call
   gatekeeper(task="", additional_args={"screening_payload": <study json>}), then
   immediately call append_screening_decision_json(..., expected_study_index=index).
5. The gatekeeper task argument is ignored by the gatekeeper wrapper; pass study
   data ONLY via additional_args. Never paste study JSON into task=.
6. Do not classify studies yourself in Orchestrator code.
7. Do not create fallback decisions or rationales.
8. Do not hard-code include/exclude labels.
9. Do not print candidate JSON or Gatekeeper responses; keep observations short.
10. If append_screening_decision_json rejects a decision, call Gatekeeper again
   for that same study rather than editing the decision in Orchestrator code.
11. Return only format_screening_progress_summary(...) as the final answer.

WORKFLOW
- Use a compact Python loop over the provided study indices.
- Inside the loop, keep only the current study payload and current Gatekeeper
  response in memory.
- The Gatekeeper managed agent run is reset for each call by smolagents, so
  each study classification remains self-contained.
"""


SCREENING_CHUNK_LOOP_ORCHESTRATOR_INSTRUCTIONS = """\
You are the Orchestrator agent for a mini-batch loop Gatekeeper screening
benchmark. You coordinate only title/abstract screening, one bounded chunk
of studies at a time.

You receive protocol context and one chunk of study indices to process. You
do NOT receive raw studies in the task itself. Retrieve the chunk only through
get_candidate_studies_chunk_json(study_indices_json), which returns only the
requested label-free candidate studies.

You have one managed agent:
1. **gatekeeper** — screens exactly one bounded study chunk

You have three utility tools:
- **get_candidate_studies_chunk_json** — returns one label-free candidate chunk
- **append_screening_chunk_decisions_json** — appends validated chunk decisions
- **format_screening_progress_summary** — returns a short Markdown summary

CRITICAL RULES
1. Never call get_candidates_json or any all-candidate retrieval helper.
2. Never place raw study data in your final answer.
3. Process only the chunk study indices listed in the task.
4. Call get_candidate_studies_chunk_json once for the listed chunk, then call
   gatekeeper(task="", additional_args={"screening_payload": <chunk json>}), then
   immediately call append_screening_chunk_decisions_json with the raw Gatekeeper
   response.
5. The gatekeeper task argument is ignored by the gatekeeper wrapper; pass chunk
   data ONLY via additional_args. Never paste chunk/study JSON into task=.
6. Do not classify studies yourself in Orchestrator code.
7. Do not create fallback decisions or rationales.
8. Do not hard-code include/exclude labels.
9. Do not print candidate JSON or Gatekeeper responses; keep observations short.
10. If append_screening_chunk_decisions_json rejects the chunk, call Gatekeeper
   again for the same chunk rather than editing decisions in Orchestrator code.
11. Return only format_screening_progress_summary(...) as the final answer.

WORKFLOW
- Parse the JSON array of chunk study indices from the task.
- Keep only the current chunk payload and current Gatekeeper response in memory.
- The chunk is intentionally bounded to reduce long-context shortcutting while
  preserving Orchestrator retrieval, delegation, and persistence behavior.
"""


def create_screening_loop_orchestrator_agent(
    orchestrator_model,
    gatekeeper_model,
    step_callbacks=None,
    logger=None,
    max_steps: int = 20,
) -> CodeAgent:
    """
    Create the looped screening Orchestrator used by the new benchmark path.
    """
    step_callbacks = with_error_abort_callback(step_callbacks)
    gatekeeper = wrap_gatekeeper(
        create_single_study_gatekeeper_agent(
            gatekeeper_model,
            step_callbacks=step_callbacks,
            logger=logger,
        ),
        fixed_task=GATEKEEPER_SINGLE_STUDY_TASK,
    )

    return CodeAgent(
        tools=[
            get_candidate_study_json,
            append_screening_decision_json,
            format_screening_progress_summary,
        ],
        model=orchestrator_model,
        managed_agents=[gatekeeper],
        name="orchestrator",
        instructions=SCREENING_LOOP_ORCHESTRATOR_INSTRUCTIONS,
        max_steps=max_steps,
        verbosity_level=2,
        executor_kwargs={"timeout_seconds": EXECUTOR_TIMEOUT_SECONDS},
        step_callbacks=step_callbacks,
        additional_authorized_imports=["json", "re", "typing", "yaml", "pandas", "numpy", "sys", "pickle"],
        logger=logger,
    )


def create_screening_chunk_loop_orchestrator_agent(
    orchestrator_model,
    gatekeeper_model,
    step_callbacks=None,
    logger=None,
    max_steps: int = 20,
) -> CodeAgent:
    """
    Create the mini-batch loop screening Orchestrator.
    """
    step_callbacks = with_error_abort_callback(step_callbacks)
    gatekeeper = wrap_gatekeeper(
        create_chunk_gatekeeper_agent(
            gatekeeper_model,
            step_callbacks=step_callbacks,
            logger=logger,
        ),
        fixed_task=GATEKEEPER_CHUNK_TASK,
    )

    return CodeAgent(
        tools=[
            get_candidate_studies_chunk_json,
            append_screening_chunk_decisions_json,
            format_screening_progress_summary,
        ],
        model=orchestrator_model,
        managed_agents=[gatekeeper],
        name="orchestrator",
        instructions=SCREENING_CHUNK_LOOP_ORCHESTRATOR_INSTRUCTIONS,
        max_steps=max_steps,
        verbosity_level=2,
        executor_kwargs={"timeout_seconds": EXECUTOR_TIMEOUT_SECONDS},
        step_callbacks=step_callbacks,
        additional_authorized_imports=["json", "re", "typing", "yaml", "pandas", "numpy", "sys", "pickle"],
        logger=logger,
    )
