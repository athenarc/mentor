"""
Orchestrator agent — manager for the full systematic-review pipeline.

Delegates to librarian, gatekeeper, miner, and critic via smolagents
``managed_agents``. Direct tools handle report formatting, evidence export,
and ``get_candidates_json`` after search. Pass ``models_by_role`` to assign a
different model per role; otherwise one shared model is reused.
"""

from smolagents import CodeAgent, Model

from mentor.settings import EXECUTOR_TIMEOUT_SECONDS
from mentor.agents.librarian import create_librarian_agent
from mentor.agents.gatekeeper import create_gatekeeper_agent
from mentor.agents.miner import create_miner_agent
from mentor.agents.critic import create_critic_agent
from mentor.tools.report_tools import (
    format_report,
    save_evidence_json,
    extract_included_studies,
)
from mentor.tools.search import get_candidates_json
from mentor.agents.prompts import load_prompt




def _require_model(
    role: str,
    *,
    models_by_role: dict[str, Model],
    shared_model: Model | None,
) -> Model:
    """Resolve role model from ``models_by_role``, else ``shared_model``."""
    model = models_by_role.get(role) or shared_model
    if model is None:
        raise ValueError(
            f"Missing model configuration for role '{role}'. "
            "Provide a shared model or define every role in models_by_role."
        )
    return model


def create_orchestrator_agent(
    model: Model | None = None,
    models_by_role: dict[str, Model] | None = None,
    step_callbacks=None,
    logger=None,
    instructions: str | None = None,
) -> CodeAgent:
    """
    Create the Orchestrator (Manager) agent with all sub-agents.

    This is the top-level agent that coordinates the full systematic
    review workflow. It delegates to the Librarian, Gatekeeper, Miner,
    and Critic agents using smolagents' managed_agents pattern.

    Args:
        model: Shared smolagents model instance used for all agents when
            ``models_by_role`` is not provided.
        models_by_role: Optional mapping from agent role to model instance.
            Supported keys are ``orchestrator``, ``librarian``, ``gatekeeper``,
            ``miner``, and ``critic``.
        step_callbacks: Optional callbacks invoked after each agent step.
            Can be a list (registered for ActionStep only) or a dict
            mapping step types to callbacks (e.g.
            ``{ActionStep: fn, PlanningStep: fn}``).
        logger: Optional ``AgentLogger`` instance shared across all
            agents for dual-write logging (terminal + file).

    Returns:
        Configured CodeAgent that manages the full workflow.
    """
    if model is None and not models_by_role:
        raise ValueError("create_orchestrator_agent requires either a shared model or models_by_role.")

    models_by_role = models_by_role or {}
    # Per-role model, falling back to the shared ``model`` when a role is omitted.
    orchestrator_model = _require_model("orchestrator", models_by_role=models_by_role, shared_model=model)
    librarian_model = _require_model("librarian", models_by_role=models_by_role, shared_model=model)
    gatekeeper_model = _require_model("gatekeeper", models_by_role=models_by_role, shared_model=model)
    miner_model = _require_model("miner", models_by_role=models_by_role, shared_model=model)
    critic_model = _require_model("critic", models_by_role=models_by_role, shared_model=model)

    # Sub-agents share logger and step_callbacks so workflow.log and activity.md
    # capture the full tree under one run directory.
    librarian = create_librarian_agent(librarian_model, step_callbacks=step_callbacks, logger=logger)
    gatekeeper = create_gatekeeper_agent(gatekeeper_model, step_callbacks=step_callbacks, logger=logger)
    miner = create_miner_agent(miner_model, step_callbacks=step_callbacks, logger=logger)
    critic = create_critic_agent(critic_model, step_callbacks=step_callbacks, logger=logger)

    return CodeAgent(
        tools=[format_report, save_evidence_json, extract_included_studies,
               get_candidates_json],
        model=orchestrator_model,
        managed_agents=[librarian, gatekeeper, miner, critic],
        instructions=instructions or load_prompt("orchestrator"),
        max_steps=10,
        planning_interval=3,  # Re-plan every 3 steps for complex workflows
        verbosity_level=2,
        executor_kwargs={"timeout_seconds": EXECUTOR_TIMEOUT_SECONDS},
        step_callbacks=step_callbacks or [],
        additional_authorized_imports=["json", "re", "os"],
        logger=logger,
    )
