"""
Gatekeeper agent — title/abstract screening.

Uses ``format_screening_tasks`` plus ``get_final_decision`` for deterministic
INCLUDE / EXCLUDE / UNCLEAR from per-criterion labels.

Uses the default ``gatekeeper`` prompt. Screening is invoked as a managed
agent: the Orchestrator calls Gatekeeper once per batch with
``additional_args['screening_payload']``.
"""

from __future__ import annotations

from typing import Sequence

from smolagents import CodeAgent, Tool

from mentor.settings import EXECUTOR_TIMEOUT_SECONDS
from mentor.agents.prompts import load_prompt
from mentor.tools.screening_tools import format_screening_tasks, get_final_decision

_DEFAULT_TOOLS = (format_screening_tasks, get_final_decision)


def create_gatekeeper_agent(
    model,
    step_callbacks=None,
    logger=None,
    *,
    tools: Sequence[Tool] | None = None,
    instructions: str | None = None,
    description: str | None = None,
) -> CodeAgent:
    """
    Create the Gatekeeper (Screening) agent.

    Args:
        model: A smolagents model instance.
        step_callbacks: Optional callbacks invoked after each agent step.
        logger: Optional AgentLogger for dual-write logging.
        tools: Tools to expose. Defaults to ``format_screening_tasks`` and
            ``get_final_decision``.
        instructions: Optional system prompt override. Defaults to the
            production ``gatekeeper`` prompt.
        description: Optional managed-agent description override.

    Returns:
        Configured CodeAgent for title/abstract screening.
    """
    selected_tools = list(tools) if tools is not None else list(_DEFAULT_TOOLS)
    if not selected_tools:
        raise ValueError("create_gatekeeper_agent requires at least one tool.")

    return CodeAgent(
        tools=selected_tools,
        model=model,
        name="gatekeeper",
        description=description
        or (
            "Screening agent. Give it candidate study JSON and it returns "
            "per-criterion assessments and INCLUDE/EXCLUDE/UNCLEAR decisions."
        ),
        instructions=instructions or load_prompt("gatekeeper"),
        max_steps=20,
        verbosity_level=2,
        executor_kwargs={"timeout_seconds": EXECUTOR_TIMEOUT_SECONDS},
        additional_authorized_imports=[
            "json",
            "re",
            "typing",
            "yaml",
            "pandas",
            "numpy",
            "pickle",
            "sys",
        ],
        step_callbacks=step_callbacks or [],
        logger=logger,
    )
