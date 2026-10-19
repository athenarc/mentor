"""
Thin orchestrator for batch Gatekeeper screening benchmarks.

Mirrors the production handoff: protocol-only task text, candidates via
``get_candidates_json``, screening delegated to a wrapped gatekeeper, decisions
saved with ``save_screening_evidence_json``. Prompts must come from
``experiments.prompts`` (not production ``mentor.agents.prompts``).
"""

from smolagents import CodeAgent

from mentor.agents.gatekeeper import create_gatekeeper_agent
from mentor.agents.wrappers import GATEKEEPER_BATCH_TASK, wrap_gatekeeper
from mentor.config import EXECUTOR_TIMEOUT_SECONDS
from mentor.errors import with_error_abort_callback
from mentor.tools.screening_benchmark_tools import (
    format_screening_summary,
    save_screening_evidence_json,
)
from mentor.tools.search import get_candidates_json


def create_screening_orchestrator_agent(
    orchestrator_model,
    gatekeeper_model,
    step_callbacks=None,
    logger=None,
    max_steps: int = 20,
    instructions: str | None = None,
    gatekeeper_instructions: str | None = None,
) -> CodeAgent:
    """
    Create the thin screening orchestrator used by the benchmark harness.

    ``instructions`` is required and should come from ``experiments.prompts``.
    """
    if not instructions:
        raise ValueError(
            "create_screening_orchestrator_agent requires instructions= "
            "(load from experiments.prompts)."
        )
    step_callbacks = with_error_abort_callback(step_callbacks)
    gatekeeper = wrap_gatekeeper(
        create_gatekeeper_agent(
            gatekeeper_model,
            step_callbacks=step_callbacks,
            logger=logger,
            instructions=gatekeeper_instructions,
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
        instructions=instructions,
        max_steps=max_steps,
        verbosity_level=2,
        executor_kwargs={"timeout_seconds": EXECUTOR_TIMEOUT_SECONDS},
        step_callbacks=step_callbacks,
        additional_authorized_imports=["json", "re", "typing", "yaml", "pandas", "numpy", "sys", "pickle"],
        logger=logger,
    )
