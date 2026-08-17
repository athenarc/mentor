"""
Bastirr run logger.

Captures two log streams for each pipeline run:

  [a] **workflow.log** — complete plain-text mirror of the Rich terminal
      output produced by smolagents.  Every ``AgentLogger.log()`` call,
      agent-tree visualisation, planning step, code action, observation,
      and final answer is written here *without* truncation.

  [b] **activity.md** — human-readable Markdown audit trail.  Each agent
      step is LLM-summarised into plain-language text so that
      non-technical readers (e.g. biomedical researchers) can understand
      what the agents did without seeing code or raw data.  Includes a
      resource-usage table and a phased timeline that groups sub-agent
      work under the orchestrator step that triggered it.

Both files are created in ``output/<timestamp>_<review>/`` alongside the
final ``report.md``.

Implementation
~~~~~~~~~~~~~~
``FileAgentLogger`` subclasses ``AgentLogger`` to **dual-write** every
Rich console call to both the terminal and a plain-text log file, giving
workflow.log the same content the user sees on screen.

``step_callbacks`` for ``ActionStep`` and ``PlanningStep`` feed an
``ActivityLogger`` instance which collects structured step data from
every agent (orchestrator + sub-agents).  At pipeline end,
``ActivityLogger.finalize()`` LLM-summarises each step and writes the
Markdown audit trail.
"""

from __future__ import annotations

from enum import StrEnum

import logging
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import IO, Any

from rich.console import Console
from smolagents import ActionStep
from smolagents.memory import PlanningStep
from smolagents.monitoring import AgentLogger, LogLevel

from bastirr.config import OUTPUT_DIR

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

AGENT_ROLES: dict[str, str] = {
    "orchestrator": "Coordinates the systematic review pipeline, delegating tasks to specialised agents",
    "librarian": "Searches for and retrieves candidate studies from the literature database",
    "gatekeeper": "Screens candidate studies for inclusion or exclusion based on the review criteria",
    "miner": "Extracts structured evidence (PICO, outcomes, effect measures) from included studies",
    "critic": "Synthesises the extracted evidence and assesses its quality",
}

_MAX_MODEL_OUTPUT_CHARS = 4000
_MAX_OBSERVATIONS_CHARS = 2000
_MAX_PLAN_CHARS = 3000
_MAX_OUTPUT_CHARS = 2000

class LoggingLevel(StrEnum):
    DEBUG = 'debug'
    INFO = 'info'
    WARNING = 'warning'
    SILENT = 'silent'

LOGGING_LEVEL_MAP = {
    LoggingLevel.DEBUG: logging.DEBUG,
    LoggingLevel.INFO: logging.INFO,
    LoggingLevel.WARNING: logging.WARNING,
    LoggingLevel.SILENT: logging.CRITICAL + 1,
}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_run_dir(review_title: str, output_root: Path | None = None) -> Path:
    """Create a timestamped output directory for this run."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_title = "".join(
        c if c.isalnum() or c in " -_" else "" for c in review_title
    )[:60].strip()
    root = output_root or OUTPUT_DIR
    run_dir = root / f"{timestamp}_{safe_title}"
    run_dir.mkdir(parents=True, exist_ok=True)
    return run_dir


def _get_agent_name(agent) -> str:
    """Extract a readable name from a smolagents agent object."""
    if agent and hasattr(agent, "name") and agent.name:
        return agent.name
    return "orchestrator"


def _truncate(text: str | None, limit: int) -> str:
    """Return *text* clipped to *limit* characters."""
    if not text:
        return ""
    if len(text) <= limit:
        return text
    return text[:limit] + "\n… [truncated]"


def _format_duration(seconds: float) -> str:
    """Human-readable duration from a float of seconds."""
    if seconds < 60:
        return f"{seconds:.0f}s"
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    if minutes < 60:
        return f"{minutes}m {secs:02d}s"
    hours = int(minutes // 60)
    mins = minutes % 60
    return f"{hours}h {mins:02d}m"


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
            highlight=True,
            force_terminal=False,
            no_color=False,
            width=120,
        )

    # -- Override the single choke-point for all structured output --
    def log(self, *args, level: int | str | LogLevel = LogLevel.INFO, **kwargs):
        if isinstance(level, str):
            level = LogLevel[level.upper()]
        if level <= self.level:
            self.console.print(*args, **kwargs)  # terminal (Rich)
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
# StepRecord / _Phase — data structures for activity logging
# ---------------------------------------------------------------------------

@dataclass
class StepRecord:
    """Raw data collected from a single agent step callback."""

    timestamp: datetime
    agent_name: str
    step_type: str  # "planning" or "action"
    step_number: int | None = None
    duration_seconds: float | None = None
    token_input: int | None = None
    token_output: int | None = None
    # Planning-specific
    plan_text: str | None = None
    # Action-specific
    tool_calls: list[str] = field(default_factory=list)
    model_output: str | None = None
    code_action: str | None = None
    observations: str | None = None
    action_output: str | None = None
    is_final_answer: bool = False
    error: str | None = None
    # Filled by ActivityLogger.finalize()
    summary: str | None = None


@dataclass
class _Phase:
    """Groups an orchestrator step with any sub-agent steps that ran inside it."""

    orchestrator_step: StepRecord | None = None
    subagent_steps: list[StepRecord] = field(default_factory=list)


# ---------------------------------------------------------------------------
# ActivityLogger — human-readable Markdown audit trail
# ---------------------------------------------------------------------------

class ActivityLogger:
    """Collects step data during a pipeline run and writes ``activity.md``.

    Usage::

        activity = ActivityLogger(run_dir, review_title)
        # ... pipeline runs, step_callbacks populate activity ...
        activity.finalize(model)   # LLM-summarise each step → write Markdown
    """

    def __init__(
            self,
            run_dir: Path,
            review_title: str,
            include_subagent_steps: bool = True,
    ):
        self.run_dir = run_dir
        self.review_title = review_title
        self.include_subagent_steps = include_subagent_steps
        self.steps: list[StepRecord] = []
        self.metadata: dict[str, str] = {}
        self.pipeline_start: datetime | None = None
        self.pipeline_end: datetime | None = None

    # -- Public API called by the runner ------------------------------------

    def log_metadata(self, key: str, value: str) -> None:
        """Store a key/value pair shown in the report header."""
        self.metadata[key] = value

    def mark_pipeline_start(self) -> None:
        self.pipeline_start = datetime.now()

    def mark_pipeline_end(self) -> None:
        self.pipeline_end = datetime.now()

    def record_action_step(self, step: ActionStep, agent=None) -> None:
        """Record an ActionStep from a smolagents callback."""
        agent_name = _get_agent_name(agent)
        duration = step.timing.duration if step.timing else None

        token_in = token_out = None
        if step.token_usage:
            token_in = getattr(step.token_usage, "input_tokens", None)
            token_out = getattr(step.token_usage, "output_tokens", None)

        tool_names: list[str] = []
        if step.tool_calls:
            tool_names = [
                tc.name if hasattr(tc, "name") else str(tc)
                for tc in step.tool_calls
            ]

        model_out = None
        if step.model_output is not None:
            model_out = (
                step.model_output
                if isinstance(step.model_output, str)
                else str(step.model_output)
            )

        self.steps.append(StepRecord(
            timestamp=datetime.now(),
            agent_name=agent_name,
            step_type="action",
            step_number=step.step_number,
            duration_seconds=duration,
            token_input=token_in,
            token_output=token_out,
            tool_calls=tool_names,
            model_output=model_out,
            code_action=step.code_action,
            observations=(
                str(step.observations) if step.observations else None
            ),
            action_output=(
                str(step.action_output)[:_MAX_OUTPUT_CHARS]
                if step.action_output else None
            ),
            is_final_answer=step.is_final_answer,
            error=str(step.error) if step.error else None,
        ))

    def record_planning_step(self, step: PlanningStep, agent=None) -> None:
        """Record a PlanningStep from a smolagents callback."""
        agent_name = _get_agent_name(agent)
        duration = step.timing.duration if step.timing else None

        token_in = token_out = None
        if step.token_usage:
            token_in = getattr(step.token_usage, "input_tokens", None)
            token_out = getattr(step.token_usage, "output_tokens", None)

        self.steps.append(StepRecord(
            timestamp=datetime.now(),
            agent_name=agent_name,
            step_type="planning",
            plan_text=getattr(step, "plan", "") or "",
            duration_seconds=duration,
            token_input=token_in,
            token_output=token_out,
        ))

    def finalize(self, model=None) -> Path:
        """Summarise every step with the LLM and write ``activity.md``.

        Args:
            model: The smolagents model to use for summarisation.
                   If *None*, a template-based fallback is used.

        Returns:
            Path to the written ``activity.md`` file.
        """
        self.mark_pipeline_end()

        for step in self.steps:
            # Skip sub-agent summarisation when they won't be shown
            if not self.include_subagent_steps and step.agent_name != "orchestrator":
                continue
            if model is not None:
                try:
                    step.summary = self._summarize_step(step, model)
                except Exception:
                    step.summary = self._fallback_summary(step)
            else:
                step.summary = self._fallback_summary(step)

        output_path = self.run_dir / "activity.md"
        output_path.write_text(self._build_markdown(), encoding="utf-8")
        return output_path

    # -- LLM summarisation --------------------------------------------------

    def _summarize_step(self, step: StepRecord, model) -> str:
        """Call the LLM with a short prompt to summarise one step."""
        from smolagents.models import ChatMessage, MessageRole

        role_desc = AGENT_ROLES.get(
            step.agent_name,
            "Agent in the systematic review pipeline",
        )

        if step.step_type == "planning":
            context = (
                    "--- Plan ---\n"
                    + _truncate(step.plan_text, _MAX_PLAN_CHARS)
            )
            activity = "Planning the next steps"
        else:
            parts: list[str] = []
            if step.model_output:
                parts.append(
                    "--- Agent reasoning and actions ---\n"
                    + _truncate(step.model_output, _MAX_MODEL_OUTPUT_CHARS)
                )
            if step.observations:
                parts.append(
                    "--- Execution result ---\n"
                    + _truncate(step.observations, _MAX_OBSERVATIONS_CHARS)
                )
            if step.error:
                parts.append(f"--- Error ---\n{str(step.error)[:500]}")
            if step.is_final_answer and step.action_output:
                parts.append(
                    "--- Final output ---\n"
                    + _truncate(step.action_output, _MAX_OUTPUT_CHARS)
                )
            context = "\n\n".join(parts) or "No detailed context available."

            if step.is_final_answer:
                activity = "Producing final output"
            elif step.tool_calls:
                activity = (
                        "Tool execution ("
                        + ", ".join(step.tool_calls)
                        + ")"
                )
            else:
                activity = "Code execution"

        prompt = (
            "You are writing a single entry in an audit trail for an automated "
            "systematic review pipeline.  Your reader is a biomedical researcher "
            "who wants to understand what the AI agents did, without seeing any "
            "code or raw data.\n\n"
            "Write a concise summary (2-4 sentences) of the following agent "
            "activity.  Use plain language.  Do NOT include any code, JSON, "
            "variable names, file paths, function calls, or technical "
            "implementation details.  Focus on what the agent intended, what it "
            "did, and what the outcome was.\n\n"
            f"Agent: {step.agent_name} — {role_desc}\n"
            f"Activity type: {activity}\n\n"
            f"{context}"
        )

        messages = [
            ChatMessage(
                role=MessageRole.USER,
                content=[{"type": "text", "text": prompt}],
            )
        ]
        response = model(messages)

        # Extract plain text from the response
        if isinstance(response.content, str):
            return response.content.strip()
        if isinstance(response.content, list):
            return " ".join(
                item.get("text", "")
                for item in response.content
                if isinstance(item, dict)
            ).strip()
        return str(response.content).strip()

    @staticmethod
    def _fallback_summary(step: StepRecord) -> str:
        """Template-based fallback when LLM summarisation is not available."""
        if step.step_type == "planning":
            first = (step.plan_text or "").strip().split("\n")[0][:200]
            return f"The {step.agent_name} created a plan. {first}"

        parts: list[str] = []
        if step.tool_calls:
            parts.append(f"Used tools: {', '.join(step.tool_calls)}.")
        if step.is_final_answer:
            parts.append("Produced the final output.")
        if step.error:
            parts.append("Encountered an error.")
        return (
                f"The {step.agent_name} executed step {step.step_number}. "
                + " ".join(parts)
        )

    # -- Markdown generation ------------------------------------------------

    def _group_into_phases(self) -> list[_Phase]:
        """Group steps into phases (one orchestrator step + its sub-agent children).

        Sub-agent callbacks fire *during* the orchestrator's code
        execution, so they appear in the list *before* the orchestrator
        ActionStep that spawned them.  We buffer sub-agent steps and
        attach them to the next orchestrator step.
        """
        phases: list[_Phase] = []
        subagent_buffer: list[StepRecord] = []

        for step in self.steps:
            if step.agent_name == "orchestrator":
                phases.append(_Phase(
                    orchestrator_step=step,
                    subagent_steps=list(subagent_buffer),
                ))
                subagent_buffer = []
            else:
                subagent_buffer.append(step)

        # Trailing sub-agent steps (shouldn't happen in normal flow)
        if subagent_buffer:
            phases.append(_Phase(subagent_steps=subagent_buffer))

        return phases

    def _build_markdown(self) -> str:
        """Generate the full ``activity.md`` content."""
        lines: list[str] = []

        # ---- Header -------------------------------------------------------
        lines.append("# Pipeline Activity Log\n")
        lines.append(f"> **Review:** {self.review_title}  ")

        if self.pipeline_start:
            lines.append(
                f"> **Date:** {self.pipeline_start.strftime('%Y-%m-%d %H:%M')}  "
            )

        if self.pipeline_start and self.pipeline_end:
            dur = (self.pipeline_end - self.pipeline_start).total_seconds()
            lines.append(f"> **Duration:** {_format_duration(dur)}  ")

        total_in = sum(s.token_input or 0 for s in self.steps)
        total_out = sum(s.token_output or 0 for s in self.steps)
        if total_in or total_out:
            lines.append(
                f"> **Total tokens:** {total_in + total_out:,} "
                f"(input: {total_in:,} / output: {total_out:,})"
            )
        lines.append("")

        if self.metadata:
            for k, v in self.metadata.items():
                lines.append(f"> **{k}:** {v}  ")
            lines.append("")

        # ---- Agent summary table ------------------------------------------
        stats = self._agent_stats()
        if stats:
            lines.append("## Resource Usage by Agent\n")
            lines.append("| Agent | Steps | Time | Tokens (in / out) |")
            lines.append("|-------|-------|------|-------------------|")
            for name, s in stats.items():
                d = _format_duration(s["dur"]) if s["dur"] else "—"
                t = (
                    f'{s["in"]:,} / {s["out"]:,}'
                    if s["in"] or s["out"]
                    else "—"
                )
                lines.append(f"| {name.title()} | {s['n']} | {d} | {t} |")
            tot_n = sum(s["n"] for s in stats.values())

            if self.pipeline_start and self.pipeline_end:
                tot_d = (self.pipeline_end - self.pipeline_start).total_seconds()
            else:
                tot_d = stats.get("orchestrator", {}).get("dur", 0.0)
            lines.append(
                f"| **Total** | **{tot_n}** | **{_format_duration(tot_d)}** "
                f"| **{total_in:,} / {total_out:,}** |"
            )
            lines.append("")

        lines.append("---\n")

        # ---- Activity timeline --------------------------------------------
        lines.append("## Activity Timeline\n")

        for i, phase in enumerate(self._group_into_phases(), 1):
            orch = phase.orchestrator_step
            subs = phase.subagent_steps

            # Orphan sub-agent steps (edge case)
            if orch is None:
                for ss in subs:
                    lines.append(
                        f"### {i}. {ss.agent_name.title()} "
                        f"— Step {ss.step_number}\n"
                    )
                    if ss.summary:
                        lines.append(f"{ss.summary}\n")
                    lines.append("---\n")
                continue

            # Phase heading
            label = self._phase_label(orch, subs)
            lines.append(f"### {i}. {label}\n")

            # Meta line (time & tokens)
            meta: list[str] = []
            if orch.timestamp:
                meta.append(orch.timestamp.strftime("%H:%M:%S"))
            if orch.duration_seconds:
                meta.append(_format_duration(orch.duration_seconds))
            tok_in = (orch.token_input or 0) + sum(
                s.token_input or 0 for s in subs
            )
            tok_out = (orch.token_output or 0) + sum(
                s.token_output or 0 for s in subs
            )
            if tok_in or tok_out:
                meta.append(f"{tok_in + tok_out:,} tokens")
            if meta:
                lines.append(f"*{' — '.join(meta)}*\n")

            # Orchestrator summary
            if orch.summary:
                lines.append(f"{orch.summary}\n")

            # Sub-agent details
            if self.include_subagent_steps and subs:
                for ss in subs:
                    heading = f"**{ss.agent_name.title()}"
                    if ss.step_number is not None:
                        heading += f" — Step {ss.step_number}"
                    if ss.is_final_answer:
                        heading += " (result)"
                    heading += ":**"
                    lines.append(f"> {heading} {ss.summary or ''}")
                lines.append("")

            if orch.error:
                lines.append(
                    f"> ⚠️ **Error:** {str(orch.error)[:300]}\n"
                )

            lines.append("---\n")

        return "\n".join(lines)

    @staticmethod
    def _phase_label(orch: StepRecord, subs: list[StepRecord]) -> str:
        """Generate a descriptive heading for one timeline phase."""
        if orch.step_type == "planning":
            return "Planning (Orchestrator)"
        sub_agents = sorted(set(s.agent_name for s in subs))
        if sub_agents:
            return (
                    "Orchestrator → "
                    + ", ".join(a.title() for a in sub_agents)
            )
        if orch.is_final_answer:
            return "Final Output (Orchestrator)"
        if orch.tool_calls:
            return f"Orchestrator ({', '.join(orch.tool_calls)})"
        return f"Orchestrator — Step {orch.step_number}"

    def _agent_stats(self) -> dict[str, dict]:
        """Compute per-agent aggregates for the summary table."""
        stats: dict[str, dict] = {}
        for s in self.steps:
            if s.agent_name not in stats:
                stats[s.agent_name] = {
                    "n": 0, "dur": 0.0, "in": 0, "out": 0,
                }
            st = stats[s.agent_name]
            st["n"] += 1
            st["dur"] += s.duration_seconds or 0.0
            st["in"] += s.token_input or 0
            st["out"] += s.token_output or 0
        return stats


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

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

    Args:
        review_title: Title of the review being processed (used in dir name).
        include_subagent_steps: If *True* (default), sub-agent steps are
            shown in the activity timeline.  If *False*, only orchestrator-
            level phases appear.
        output_root: Optional directory under which the run directory is created.
        run_name: Optional name for the run directory. Defaults to review_title.

    Returns:
        ``(run_dir, agent_logger, activity_logger)``
    """
    run_dir = _make_run_dir(run_name or review_title, output_root=output_root)

    # --- Workflow: FileAgentLogger (mirrors terminal → file) ---
    wf_file = open(run_dir / "workflow.log", "w", encoding="utf-8")
    agent_logger = FileAgentLogger(level=LogLevel.DEBUG, log_file=wf_file)

    # --- Activity logger (collects step data for activity.md) ---
    activity_logger = ActivityLogger(
        run_dir=run_dir,
        review_title=review_title,
        include_subagent_steps=include_subagent_steps,
    )

    # Log run metadata to the terminal/workflow.log
    agent_logger.log(
        f"{'=' * 70}\nBASTIRR PIPELINE RUN\n"
        f"Review: {review_title}\n"
        f"Run directory: {run_dir}\n"
        f"Started: {datetime.now().isoformat()}\n"
        f"{'=' * 70}",
        level=LogLevel.INFO,
    )

    return run_dir, agent_logger, activity_logger


def setup_tool_logger(logger: logging.Logger, logging_level: int = logging.INFO):
    if logger.handlers:
        return logger

    logger.setLevel(logging_level)

    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging_level)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    stream_handler.setFormatter(formatter)

    logger.addHandler(stream_handler)
    logger.propagate = False

    return logger


def make_step_callbacks(activity_logger: ActivityLogger) -> dict:
    """Create smolagents ``step_callbacks`` dict for activity logging.

    Registers callbacks for **both** ``ActionStep`` (code/tool execution)
    and ``PlanningStep`` (agent planning output).  The collected data is
    used by ``ActivityLogger.finalize()`` to produce ``activity.md``.
    """

    def _action_callback(
            memory_step: ActionStep, agent=None, **kwargs,
    ):
        activity_logger.record_action_step(memory_step, agent)

    def _planning_callback(
            memory_step: PlanningStep, agent=None, **kwargs,
    ):
        activity_logger.record_planning_step(memory_step, agent)

    return {
        ActionStep: _action_callback,
        PlanningStep: _planning_callback,
    }
