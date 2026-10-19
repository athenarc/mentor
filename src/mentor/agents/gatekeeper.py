"""
Gatekeeper agent — title/abstract screening.

Uses ``screen_study`` and ``batch_screen_studies`` to format screening tasks;
the LLM applies ``selection_criteria`` and returns INCLUDE/EXCLUDE JSON.

``create_single_study_gatekeeper_agent`` and ``create_chunk_gatekeeper_agent``
are experiment-only variants (prompts from ``experiments.prompts``) used by loop
benchmark orchestrators.
"""

from smolagents import CodeAgent

from mentor.config import EXECUTOR_TIMEOUT_SECONDS
from mentor.agents.prompts import load_prompt
from mentor.tools.screening_tools import batch_screen_studies, screen_study


def create_gatekeeper_agent(
    model,
    step_callbacks=None,
    logger=None,
    instructions: str | None = None,
) -> CodeAgent:
    """
    Create the Gatekeeper (Screening) agent.

    Args:
        model: A smolagents model instance.
        step_callbacks: Optional callbacks invoked after each agent step.
        logger: Optional AgentLogger for dual-write logging.
        instructions: Optional system prompt override. Defaults to the
            production ``gatekeeper`` prompt.

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
        instructions=instructions or load_prompt("gatekeeper"),
        max_steps=20,
        verbosity_level=2,
        executor_kwargs={"timeout_seconds": EXECUTOR_TIMEOUT_SECONDS},
        additional_authorized_imports=["json", "re", "typing", "yaml", "pandas", "numpy", "pickle", "sys"],
        step_callbacks=step_callbacks or [],
        logger=logger,
    )


def create_single_study_gatekeeper_agent(
    model,
    step_callbacks=None,
    logger=None,
    instructions: str | None = None,
) -> CodeAgent:
    """
    Create a Gatekeeper agent constrained to one study per managed call.

    Experiment callers must pass ``instructions`` (typically from
    ``experiments.prompts``). There is no production default for this mode.
    """
    if not instructions:
        raise ValueError(
            "create_single_study_gatekeeper_agent requires instructions= "
            "(load from experiments.prompts)."
        )
    return CodeAgent(
        tools=[screen_study],
        model=model,
        name="gatekeeper",
        description=(
            "Single-study screening agent. Give it one study plus the review "
            "protocol and it returns exactly one INCLUDE/EXCLUDE decision."
        ),
        instructions=instructions,
        max_steps=20,
        verbosity_level=2,
        executor_kwargs={"timeout_seconds": EXECUTOR_TIMEOUT_SECONDS},
        additional_authorized_imports=["json", "re", "typing", "yaml", "pandas", "numpy", "pickle", "sys"],
        step_callbacks=step_callbacks or [],
        logger=logger,
    )


def create_chunk_gatekeeper_agent(
    model,
    step_callbacks=None,
    logger=None,
    instructions: str | None = None,
) -> CodeAgent:
    """
    Create a Gatekeeper agent constrained to one bounded study chunk per call.

    Experiment callers must pass ``instructions`` (typically from
    ``experiments.prompts``).
    """
    if not instructions:
        raise ValueError(
            "create_chunk_gatekeeper_agent requires instructions= "
            "(load from experiments.prompts)."
        )
    return CodeAgent(
        tools=[batch_screen_studies],
        model=model,
        name="gatekeeper",
        description=(
            "Mini-batch screening agent. Give it one bounded study chunk plus "
            "the review protocol and it returns one decision per chunk study."
        ),
        instructions=instructions,
        max_steps=20,
        verbosity_level=2,
        executor_kwargs={"timeout_seconds": EXECUTOR_TIMEOUT_SECONDS},
        additional_authorized_imports=["json", "re", "typing", "yaml", "pandas", "numpy", "pickle", "sys"],
        step_callbacks=step_callbacks or [],
        logger=logger,
    )
