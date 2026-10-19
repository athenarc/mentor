"""Wire FileAgentLogger + ActivityLogger for a Mentor pipeline run."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from smolagents import ActionStep
from smolagents.memory import PlanningStep
from smolagents.monitoring import LogLevel

from mentor.logging.activity import ActivityLogger
from mentor.logging.file_logger import FileAgentLogger
from mentor.logging.helpers import make_run_dir


def setup_run_logging(
    review_title: str,
    include_subagent_steps: bool = True,
    output_root: Path | None = None,
    run_name: str | None = None,
) -> tuple[Path, FileAgentLogger, ActivityLogger]:
    """Set up file-based logging for a pipeline run.

    Creates a run directory and configures:
      - A ``FileAgentLogger`` that mirrors terminal output → workflow.log
      - An ``ActivityLogger`` that collects step data → activity.md

    Returns:
        ``(run_dir, agent_logger, activity_logger)``
    """
    run_dir = make_run_dir(run_name or review_title, output_root=output_root)

    wf_file = open(run_dir / "workflow.log", "w", encoding="utf-8")
    agent_logger = FileAgentLogger(level=LogLevel.DEBUG, log_file=wf_file)

    activity_logger = ActivityLogger(
        run_dir=run_dir,
        review_title=review_title,
        include_subagent_steps=include_subagent_steps,
    )

    agent_logger.log(
        f"{'=' * 70}\nMENTOR PIPELINE RUN\n"
        f"Review: {review_title}\n"
        f"Run directory: {run_dir}\n"
        f"Started: {datetime.now().isoformat()}\n"
        f"{'=' * 70}",
        level=LogLevel.INFO,
    )

    return run_dir, agent_logger, activity_logger


def make_step_callbacks(activity_logger: ActivityLogger) -> dict:
    """Create smolagents ``step_callbacks`` dict for activity logging."""

    def _action_callback(memory_step: ActionStep, agent=None, **kwargs):
        activity_logger.record_action_step(memory_step, agent)

    def _planning_callback(memory_step: PlanningStep, agent=None, **kwargs):
        activity_logger.record_planning_step(memory_step, agent)

    return {
        ActionStep: _action_callback,
        PlanningStep: _planning_callback,
    }
