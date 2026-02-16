"""
Bastirr run logger.

Captures two log streams for each pipeline run:

  [a] **workflow.log** — complete plain-text mirror of the Rich terminal
      output produced by smolagents.  Every ``AgentLogger.log()`` call,
      agent-tree visualisation, planning step, code action, observation,
      and final answer is written here *without* truncation.

  [b] **decisions.log** — structured decisions at each step: orchestrator
      plan, agent outputs, screening decisions, extraction results,
      synthesis, token usage.

Both files are created in ``output/<timestamp>_<review>/`` alongside the
final ``report.md``.

Implementation
~~~~~~~~~~~~~~
Instead of relying solely on ``step_callbacks`` (which only fires *after*
each step and can miss planning output, agent-tree visualisations, system
prompts, etc.), we subclass ``AgentLogger`` to **dual-write** every Rich
console call to both the terminal and a plain-text log file.  This gives
workflow.log the same content the user sees on screen.

``step_callbacks`` are still used for the structured **decisions.log**.
We register callbacks for *both* ``ActionStep`` and ``PlanningStep`` so
that planning output is also captured.
"""

from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path
from typing import IO

from rich.console import Console
from smolagents import ActionStep
from smolagents.memory import PlanningStep
from smolagents.monitoring import AgentLogger, LogLevel

from bastirr.config import OUTPUT_DIR


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_run_dir(review_title: str) -> Path:
    """Create a timestamped output directory for this run."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_title = "".join(
        c if c.isalnum() or c in " -_" else "" for c in review_title
    )[:60].strip()
    run_dir = OUTPUT_DIR / f"{timestamp}_{safe_title}"
    run_dir.mkdir(parents=True, exist_ok=True)
    return run_dir


# ---------------------------------------------------------------------------
# FileAgentLogger — dual-write AgentLogger
# ---------------------------------------------------------------------------

class FileAgentLogger(AgentLogger):
    """``AgentLogger`` subclass that mirrors *all* output to a log file.

    Every call to ``log()`` (which ``log_markdown``, ``log_code``,
    ``log_rule``, ``log_task``, ``log_error`` all delegate to) is
    rendered twice:

    * to the **terminal** via the inherited Rich ``Console`` (with
      colours / formatting), and
    * to a **plain-text log file** via a second ``Console`` instance
      (``no_color=True``, wide columns for readability).

    ``visualize_agent_tree()`` also writes to both outputs.
    """

    def __init__(self, level: LogLevel, log_file: IO[str]):
        super().__init__(level=level)
        self._log_file = log_file
        self._file_console = Console(
            file=self._log_file,
            highlight=False,
            force_terminal=False,
            no_color=True,
            width=120,
        )

    # -- Override the single choke-point for all structured output --
    def log(self, *args, level: int | str | LogLevel = LogLevel.INFO, **kwargs):
        if isinstance(level, str):
            level = LogLevel[level.upper()]
        if level <= self.level:
            self.console.print(*args, **kwargs)      # terminal (Rich)
            self._file_console.print(*args, **kwargs)  # file (plain text)

    # -- Agent tree is printed directly to self.console; mirror it --
    def visualize_agent_tree(self, agent):
        super().visualize_agent_tree(agent)
        # Re-render the tree to the file console
        self._render_agent_tree_to_file(agent)

    def _render_agent_tree_to_file(self, agent):
        """Reproduce a simplified text version of the agent tree."""
        from rich.tree import Tree

        def _build(parent, agent_obj):
            if agent_obj.tools:
                for name in agent_obj.tools:
                    parent.add(f"[tool] {name}")
            if agent_obj.managed_agents:
                for name, ma in agent_obj.managed_agents.items():
                    branch = parent.add(f"{name} | {ma.__class__.__name__} | {ma.model.model_id}")
                    branch.add(f"description: {ma.description}")
                    _build(branch, ma)

        headline = f"{agent.__class__.__name__} | {agent.model.model_id}"
        tree = Tree(headline)
        _build(tree, agent)
        self._file_console.print(tree)

    def close(self):
        """Flush and close the log file."""
        self._log_file.flush()
        self._log_file.close()


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def setup_run_logging(
    review_title: str,
) -> tuple[Path, FileAgentLogger, logging.Logger]:
    """
    Set up file-based logging for a pipeline run.

    Creates a run directory and configures:
      - A ``FileAgentLogger`` that mirrors terminal output → workflow.log
      - A standard ``logging.Logger`` for structured decisions → decisions.log

    Args:
        review_title: Title of the review being processed (used in dir name).

    Returns:
        ``(run_dir, agent_logger, decisions_logger)``
    """
    run_dir = _make_run_dir(review_title)

    # --- Workflow: FileAgentLogger (mirrors terminal → file) ---
    wf_file = open(run_dir / "workflow.log", "w", encoding="utf-8")
    agent_logger = FileAgentLogger(level=LogLevel.DEBUG, log_file=wf_file)

    # --- Decisions logger (structured, key decisions only) ---
    decisions_logger = logging.getLogger("bastirr.decisions")
    decisions_logger.setLevel(logging.INFO)
    decisions_logger.handlers.clear()
    decisions_logger.propagate = False

    dec_handler = logging.FileHandler(run_dir / "decisions.log", encoding="utf-8")
    dec_handler.setLevel(logging.INFO)
    dec_handler.setFormatter(logging.Formatter("%(asctime)s | %(message)s"))
    decisions_logger.addHandler(dec_handler)

    # Log run metadata
    agent_logger.log(
        f"{'=' * 70}\nBASTIRR PIPELINE RUN\n"
        f"Review: {review_title}\n"
        f"Run directory: {run_dir}\n"
        f"Started: {datetime.now().isoformat()}\n"
        f"{'=' * 70}",
        level=LogLevel.INFO,
    )

    decisions_logger.info("=" * 70)
    decisions_logger.info("BASTIRR DECISIONS LOG")
    decisions_logger.info(f"Review: {review_title}")
    decisions_logger.info(f"Started: {datetime.now().isoformat()}")
    decisions_logger.info("=" * 70)

    return run_dir, agent_logger, decisions_logger


def make_step_callbacks(
    decisions_logger: logging.Logger,
) -> dict:
    """
    Create smolagents ``step_callbacks`` dict for structured decision logging.

    Registers callbacks for **both** ``ActionStep`` (code/tool execution)
    and ``PlanningStep`` (agent planning output).  The workflow.log capture
    is handled by ``FileAgentLogger``; these callbacks populate only
    ``decisions.log``.

    Args:
        decisions_logger: Python logger for the decisions file.

    Returns:
        A dict suitable for ``step_callbacks`` parameter::

            {ActionStep: callback, PlanningStep: callback}
    """

    def _action_callback(memory_step: ActionStep, agent=None, **kwargs):
        step_num = memory_step.step_number
        agent_name = (
            agent.name
            if agent and hasattr(agent, "name") and agent.name
            else "orchestrator"
        )

        # Tool calls
        if memory_step.tool_calls:
            tool_names = [
                tc.name if hasattr(tc, "name") else str(tc)
                for tc in memory_step.tool_calls
            ]
            decisions_logger.info(
                f"[{agent_name}] Step {step_num} | Tools: {', '.join(tool_names)}"
            )

        # Code action
        if memory_step.code_action:
            decisions_logger.info(
                f"[{agent_name}] Step {step_num} | Code action:\n{memory_step.code_action}"
            )

        # Errors
        if memory_step.error:
            decisions_logger.info(
                f"[{agent_name}] Step {step_num} | ERROR: {memory_step.error}"
            )

        # Final answer
        if memory_step.is_final_answer:
            output_str = str(memory_step.action_output) if memory_step.action_output else ""
            preview = (output_str[:2000] + "\n... [truncated]") if len(output_str) > 2000 else output_str
            decisions_logger.info(
                f"[{agent_name}] Step {step_num} | FINAL ANSWER:\n{preview}"
            )

        # Token usage
        if memory_step.token_usage:
            usage = memory_step.token_usage
            decisions_logger.info(
                f"[{agent_name}] Step {step_num} | Tokens — "
                f"input: {getattr(usage, 'input_tokens', 'N/A')}, "
                f"output: {getattr(usage, 'output_tokens', 'N/A')}"
            )

    def _planning_callback(memory_step: PlanningStep, agent=None, **kwargs):
        agent_name = (
            agent.name
            if agent and hasattr(agent, "name") and agent.name
            else "orchestrator"
        )
        plan_text = getattr(memory_step, "plan", "") or ""
        preview = (plan_text[:2000] + "\n... [truncated]") if len(plan_text) > 2000 else plan_text
        decisions_logger.info(f"[{agent_name}] PLAN:\n{preview}")

        if memory_step.token_usage:
            usage = memory_step.token_usage
            decisions_logger.info(
                f"[{agent_name}] Plan tokens — "
                f"input: {getattr(usage, 'input_tokens', 'N/A')}, "
                f"output: {getattr(usage, 'output_tokens', 'N/A')}"
            )

    return {
        ActionStep: _action_callback,
        PlanningStep: _planning_callback,
    }
