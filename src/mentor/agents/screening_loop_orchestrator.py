"""
Looped orchestrators for per-study and mini-batch screening benchmarks.

Separate from the batch ``screening_orchestrator``: each orchestrator step
fetches one study or chunk via search getter tools, calls gatekeeper through
``wrap_gatekeeper``, and appends decisions incrementally to ``evidence.json``.
"""

from smolagents import CodeAgent

from mentor.agents.gatekeeper import create_gatekeeper_agent
from mentor.agents.wrappers import (
    GATEKEEPER_CHUNK_TASK,
    GATEKEEPER_SINGLE_STUDY_TASK,
    wrap_gatekeeper,
)
from mentor.config import EXECUTOR_TIMEOUT_SECONDS
from mentor.errors import with_error_abort_callback
from mentor.tools.screening_benchmark_tools import (
    append_screening_chunk_decisions_json,
    append_screening_decision_json,
    format_screening_progress_summary,
)
from mentor.tools.search import (
    get_candidate_studies_chunk_json,
    get_candidate_study_json,
)


def create_screening_loop_orchestrator_agent(
    orchestrator_model,
    gatekeeper_model,
    step_callbacks=None,
    logger=None,
    max_steps: int = 20,
    instructions: str | None = None,
    gatekeeper_instructions: str | None = None,
) -> CodeAgent:
    """Create the looped screening Orchestrator used by the loop benchmark path."""
    if not instructions:
        raise ValueError(
            "create_screening_loop_orchestrator_agent requires instructions= "
            "(load from experiments.prompts)."
        )
    if not gatekeeper_instructions:
        raise ValueError(
            "create_screening_loop_orchestrator_agent requires "
            "gatekeeper_instructions= (load from experiments.prompts)."
        )
    step_callbacks = with_error_abort_callback(step_callbacks)
    gatekeeper = wrap_gatekeeper(
        create_gatekeeper_agent(
            gatekeeper_model,
            step_callbacks=step_callbacks,
            logger=logger,
            instructions=gatekeeper_instructions,
            description=(
                "Single-study screening agent. Give it one study plus the "
                "review protocol and it returns exactly one INCLUDE/EXCLUDE "
                "decision."
            ),
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
        instructions=instructions,
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
    instructions: str | None = None,
    gatekeeper_instructions: str | None = None,
) -> CodeAgent:
    """Create the mini-batch loop screening Orchestrator."""
    if not instructions:
        raise ValueError(
            "create_screening_chunk_loop_orchestrator_agent requires instructions= "
            "(load from experiments.prompts)."
        )
    if not gatekeeper_instructions:
        raise ValueError(
            "create_screening_chunk_loop_orchestrator_agent requires "
            "gatekeeper_instructions= (load from experiments.prompts)."
        )
    step_callbacks = with_error_abort_callback(step_callbacks)
    gatekeeper = wrap_gatekeeper(
        create_gatekeeper_agent(
            gatekeeper_model,
            step_callbacks=step_callbacks,
            logger=logger,
            instructions=gatekeeper_instructions,
            description=(
                "Mini-batch screening agent. Give it one bounded study chunk "
                "plus the review protocol and it returns one decision per "
                "chunk study."
            ),
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
        instructions=instructions,
        max_steps=max_steps,
        verbosity_level=2,
        executor_kwargs={"timeout_seconds": EXECUTOR_TIMEOUT_SECONDS},
        step_callbacks=step_callbacks,
        additional_authorized_imports=["json", "re", "typing", "yaml", "pandas", "numpy", "sys", "pickle"],
        logger=logger,
    )
