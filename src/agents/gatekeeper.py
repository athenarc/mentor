"""
Gatekeeper agent — title/abstract screening.

Uses ``screen_studies`` to format screening tasks; the LLM applies
``selection_criteria`` and returns INCLUDE/EXCLUDE JSON.

Uses the default ``gatekeeper`` prompt. Screening is invoked via the
``screen_candidates`` tool (batched Gatekeeper calls).
"""

from __future__ import annotations

from typing import Sequence

from smolagents import CodeAgent, Tool

from mentor.settings import EXECUTOR_TIMEOUT_SECONDS
from mentor.agents.prompts import load_prompt
from mentor.tools.screening_tools import screen_studies

_DEFAULT_TOOLS = (screen_studies,)


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
        tools: Tools to expose. Defaults to ``screen_studies``.
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
            "screening decisions (INCLUDE/EXCLUDE)."
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
