"""
Bastirr run logger.

Captures two log streams for each pipeline run:
  [a] workflow.log — full terminal-style workflow output (what you'd see
      if watching the agents work in real time).
  [b] decisions.log — structured decisions at each step: orchestrator plan,
      agent outputs, screening decisions, extraction results, synthesis.

Both logs are written to ``output/<timestamp>_<review>/`` alongside the
final report.
"""

import json
import logging
from datetime import datetime
from pathlib import Path

from smolagents import ActionStep

from bastirr.config import OUTPUT_DIR


def _make_run_dir(review_title: str) -> Path:
    """Create a timestamped output directory for this run."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_title = "".join(
        c if c.isalnum() or c in " -_" else "" for c in review_title
    )[:60].strip()
    run_dir = OUTPUT_DIR / f"{timestamp}_{safe_title}"
    run_dir.mkdir(parents=True, exist_ok=True)
    return run_dir


def setup_run_logging(review_title: str) -> tuple[Path, logging.Logger, logging.Logger]:
    """
    Set up file-based logging for a pipeline run.

    Creates a run directory and configures two loggers:
      - ``workflow`` — full verbose output (mirrors terminal)
      - ``decisions`` — high-level decisions and agent outputs only

    Args:
        review_title: Title of the review being processed (used in dir name).

    Returns:
        (run_dir, workflow_logger, decisions_logger)
    """
    run_dir = _make_run_dir(review_title)

    # --- Workflow logger (verbose, everything) ---
    workflow_logger = logging.getLogger("bastirr.workflow")
    workflow_logger.setLevel(logging.DEBUG)
    workflow_logger.handlers.clear()
    workflow_logger.propagate = False

    wf_handler = logging.FileHandler(run_dir / "workflow.log", encoding="utf-8")
    wf_handler.setLevel(logging.DEBUG)
    wf_handler.setFormatter(
        logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
    )
    workflow_logger.addHandler(wf_handler)

    # Also stream workflow to console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(
        logging.Formatter("%(asctime)s [%(name)s] %(levelname)s: %(message)s")
    )
    workflow_logger.addHandler(console_handler)

    # --- Decisions logger (structured, key decisions only) ---
    decisions_logger = logging.getLogger("bastirr.decisions")
    decisions_logger.setLevel(logging.INFO)
    decisions_logger.handlers.clear()
    decisions_logger.propagate = False

    dec_handler = logging.FileHandler(run_dir / "decisions.log", encoding="utf-8")
    dec_handler.setLevel(logging.INFO)
    dec_handler.setFormatter(
        logging.Formatter("%(asctime)s | %(message)s")
    )
    decisions_logger.addHandler(dec_handler)

    # Log run metadata
    workflow_logger.info("=" * 70)
    workflow_logger.info("BASTIRR PIPELINE RUN")
    workflow_logger.info(f"Review: {review_title}")
    workflow_logger.info(f"Run directory: {run_dir}")
    workflow_logger.info("=" * 70)

    decisions_logger.info("=" * 70)
    decisions_logger.info("BASTIRR DECISIONS LOG")
    decisions_logger.info(f"Review: {review_title}")
    decisions_logger.info(f"Started: {datetime.now().isoformat()}")
    decisions_logger.info("=" * 70)

    return run_dir, workflow_logger, decisions_logger


def make_step_callback(
    workflow_logger: logging.Logger,
    decisions_logger: logging.Logger,
):
    """
    Create a smolagents ``step_callbacks`` function that logs each agent step.

    The callback is called after every ``ActionStep``. It writes:
      - Full step details (model output, code, observations) → workflow.log
      - Key decisions (tool calls, errors, final answers) → decisions.log

    Args:
        workflow_logger: Logger for full workflow output.
        decisions_logger: Logger for structured decisions.

    Returns:
        A callback function compatible with smolagents ``step_callbacks``.
    """

    def _step_callback(memory_step: ActionStep, agent=None, **kwargs):
        step_num = memory_step.step_number
        agent_name = agent.name if agent and hasattr(agent, "name") and agent.name else "orchestrator"

        # --- Workflow: full details ---
        workflow_logger.debug(f"--- [{agent_name}] Step {step_num} ---")

        if memory_step.model_output:
            # Truncate very long model outputs for the workflow log
            output = memory_step.model_output
            if len(output) > 5000:
                output = output[:5000] + "\n... [truncated]"
            workflow_logger.debug(f"[{agent_name}] LLM output:\n{output}")

        if memory_step.code_action:
            workflow_logger.info(f"[{agent_name}] Step {step_num} — code action:\n{memory_step.code_action}")

        if memory_step.tool_calls:
            for tc in memory_step.tool_calls:
                tool_name = tc.name if hasattr(tc, "name") else str(tc)
                workflow_logger.info(f"[{agent_name}] Step {step_num} — tool call: {tool_name}")

        if memory_step.observations:
            obs = memory_step.observations
            if len(obs) > 3000:
                obs = obs[:3000] + "\n... [truncated]"
            workflow_logger.debug(f"[{agent_name}] Observations:\n{obs}")

        if memory_step.error:
            workflow_logger.warning(f"[{agent_name}] Step {step_num} — ERROR: {memory_step.error}")

        if memory_step.is_final_answer:
            output_str = str(memory_step.action_output) if memory_step.action_output else ""
            if len(output_str) > 2000:
                output_str = output_str[:2000] + "\n... [truncated]"
            workflow_logger.info(f"[{agent_name}] FINAL ANSWER:\n{output_str}")

        # --- Decisions: structured summary ---
        if memory_step.tool_calls:
            tool_names = []
            for tc in memory_step.tool_calls:
                tool_names.append(tc.name if hasattr(tc, "name") else str(tc))
            decisions_logger.info(
                f"[{agent_name}] Step {step_num} | Tools called: {', '.join(tool_names)}"
            )

        if memory_step.error:
            decisions_logger.info(
                f"[{agent_name}] Step {step_num} | ERROR: {memory_step.error}"
            )

        if memory_step.is_final_answer:
            output_str = str(memory_step.action_output) if memory_step.action_output else ""
            # For decisions log, try to capture the key structure
            preview = output_str[:1000] + "..." if len(output_str) > 1000 else output_str
            decisions_logger.info(
                f"[{agent_name}] Step {step_num} | FINAL ANSWER:\n{preview}"
            )

        # Log token usage if available
        if memory_step.token_usage:
            usage = memory_step.token_usage
            decisions_logger.info(
                f"[{agent_name}] Step {step_num} | Tokens — "
                f"input: {getattr(usage, 'input_tokens', 'N/A')}, "
                f"output: {getattr(usage, 'output_tokens', 'N/A')}"
            )

    return _step_callback
