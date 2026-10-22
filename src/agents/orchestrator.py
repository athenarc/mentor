"""
Orchestrator agent — manager for the systematic-review pipeline.

One factory supports:
- ``mode="full"``: librarian → screen_candidates → miner → critic → report
- ``mode="screening-only"``: screen_candidates only (candidates preloaded)

Screening always goes through the Python ``screen_candidates`` tool, which
batches Gatekeeper calls by ``batch_size`` (None = all, 1 = single-study, N = chunks).
"""

from __future__ import annotations

from smolagents import CodeAgent, Model

from mentor.settings import EXECUTOR_TIMEOUT_SECONDS
from mentor.agents.librarian import create_librarian_agent
from mentor.agents.gatekeeper import create_gatekeeper_agent
from mentor.agents.miner import create_miner_agent
from mentor.agents.critic import create_critic_agent
from mentor.agents.wrappers.gatekeeper import GATEKEEPER_TASK, wrap_gatekeeper
from mentor.tools.report_tools import (
    format_report,
    save_evidence_json,
    extract_included_studies,
)
from mentor.tools.search import get_candidates_json
from mentor.tools.screening_loop import make_screen_candidates_tool
from mentor.tools.screening_persistence import format_screening_progress_summary
from mentor.agents.prompts import resolve_prompt


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
    *,
    mode: str = "full",
    batch_size: int | None = None,
    output_dir: str | None = None,
    max_steps: int | None = None,
    max_batch_attempts: int = 2,
    prompt_paths: dict[str, str] | None = None,
) -> CodeAgent:
    """
    Create the Orchestrator agent.

    Args:
        model: Shared smolagents model used for all roles when
            ``models_by_role`` is not provided.
        models_by_role: Optional mapping from agent role to model instance.
            Supported keys: ``orchestrator``, ``librarian``, ``gatekeeper``,
            ``miner``, ``critic``.
        step_callbacks: Optional callbacks invoked after each agent step.
        logger: Optional ``AgentLogger`` shared across agents.
        instructions: Optional orchestrator prompt override (wins over
            ``prompt_paths`` for the orchestrator role).
        mode: ``"full"`` (search → screen → extract → synthesize) or
            ``"screening-only"`` (Gatekeeper screening only).
        batch_size: Studies per Gatekeeper call. ``None`` = all studies;
            ``1`` = one study at a time; ``N`` = chunks of N.
        output_dir: Directory for ``evidence.json`` / progress (required).
        max_steps: Orchestrator step budget. Defaults: 10 (full), 6
            (screening-only).
        max_batch_attempts: Retries per screening batch before fail-closed.
        prompt_paths: Optional role → prompt file path overrides
            (``librarian``, ``gatekeeper``, ``miner``, ``critic``,
            ``orchestrator``). One ``orchestrator`` path covers both modes;
            packaged defaults remain ``orchestrator.md`` (full) and
            ``orchestrator_screening-only.md`` (screening-only). Missing roles
            use packaged defaults.

    Returns:
        Configured CodeAgent.
    """
    if model is None and not models_by_role:
        raise ValueError(
            "create_orchestrator_agent requires either a shared model or models_by_role."
        )
    mode_key = str(mode).strip().lower()
    if mode_key not in {"full", "screening-only"}:
        raise ValueError(
            f"mode must be 'full' or 'screening-only', got {mode!r}"
        )
    mode = mode_key
    if output_dir is None:
        raise ValueError("create_orchestrator_agent requires output_dir for screening persistence.")
    if batch_size is not None and batch_size < 1:
        raise ValueError("batch_size must be at least 1 when provided")

    paths = prompt_paths or {}
    models_by_role = models_by_role or {}
    orchestrator_model = _require_model(
        "orchestrator", models_by_role=models_by_role, shared_model=model
    )
    gatekeeper_model = _require_model(
        "gatekeeper", models_by_role=models_by_role, shared_model=model
    )

    gatekeeper = wrap_gatekeeper(
        create_gatekeeper_agent(
            gatekeeper_model,
            step_callbacks=step_callbacks,
            logger=logger,
            instructions=resolve_prompt("gatekeeper", paths),
        ),
        fixed_task=GATEKEEPER_TASK,
    )
    screen_candidates = make_screen_candidates_tool(
        gatekeeper,
        batch_size=batch_size,
        output_dir=output_dir,
        max_batch_attempts=max_batch_attempts,
    )

    if mode == "screening-only":
        resolved_max_steps = max_steps if max_steps is not None else 6
        return CodeAgent(
            tools=[screen_candidates, format_screening_progress_summary],
            model=orchestrator_model,
            managed_agents=[],
            instructions=instructions
            or resolve_prompt(
                "orchestrator",
                paths,
                default="orchestrator_screening-only",
            ),
            max_steps=resolved_max_steps,
            verbosity_level=2,
            executor_kwargs={"timeout_seconds": EXECUTOR_TIMEOUT_SECONDS},
            step_callbacks=step_callbacks or [],
            additional_authorized_imports=["json", "re", "os"],
            logger=logger,
        )

    librarian_model = _require_model(
        "librarian", models_by_role=models_by_role, shared_model=model
    )
    miner_model = _require_model(
        "miner", models_by_role=models_by_role, shared_model=model
    )
    critic_model = _require_model(
        "critic", models_by_role=models_by_role, shared_model=model
    )

    librarian = create_librarian_agent(
        librarian_model,
        step_callbacks=step_callbacks,
        logger=logger,
        instructions=resolve_prompt("librarian", paths),
    )
    miner = create_miner_agent(
        miner_model,
        step_callbacks=step_callbacks,
        logger=logger,
        instructions=resolve_prompt("miner", paths),
    )
    critic = create_critic_agent(
        critic_model,
        step_callbacks=step_callbacks,
        logger=logger,
        instructions=resolve_prompt("critic", paths),
    )

    resolved_max_steps = max_steps if max_steps is not None else 10
    return CodeAgent(
        tools=[
            format_report,
            save_evidence_json,
            extract_included_studies,
            get_candidates_json,
            screen_candidates,
        ],
        model=orchestrator_model,
        managed_agents=[librarian, miner, critic],
        instructions=instructions or resolve_prompt("orchestrator", paths),
        max_steps=resolved_max_steps,
        planning_interval=3,
        verbosity_level=2,
        executor_kwargs={"timeout_seconds": EXECUTOR_TIMEOUT_SECONDS},
        step_callbacks=step_callbacks or [],
        additional_authorized_imports=["json", "re", "os"],
        logger=logger,
    )
