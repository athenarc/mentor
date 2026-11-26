"""Activity.md audit trail: step records and LLM-summarised timeline."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

from smolagents import ActionStep
from smolagents.memory import PlanningStep

from mentor.logging.helpers import (
    format_duration,
    get_agent_name,
    truncate,
)
from mentor.logging.provider_usage import extract_call_usage, raw_completion_from_step


def _usage_bag(
    *,
    input_tokens: int | None,
    output_tokens: int | None,
    duration: float | None,
    cost: float | None,
    provider: str | None = None,
    include_provider: bool = False,
) -> dict:
    bag = {
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "duration": duration,
        "cost": cost,
    }
    if include_provider:
        bag["provider"] = provider
    return bag


def _usage_block(node: dict) -> dict:
    """Return the node's ``usage`` object (``self`` / optional ``total``)."""
    usage = node.get("usage")
    return usage if isinstance(usage, dict) else {}


def _inclusive_usage(node: dict) -> dict:
    """Return inclusive usage: ``usage.total`` when present, else ``usage.self``."""
    usage = _usage_block(node)
    total = usage.get("total")
    if isinstance(total, dict):
        return total
    self_usage = usage.get("self")
    return self_usage if isinstance(self_usage, dict) else {}


def with_nested_steps(parent: dict, children: list[dict]) -> dict:
    """Attach children and add parent ``usage.total`` (leaves omit ``total``).

    ``usage.total.duration`` is the parent's wall-clock. ``usage.self.duration``
    becomes exclusive time (wall minus child inclusive durations). Tokens/cost
    totals roll up ``self + sum(child inclusive)``.
    """
    usage = dict(_usage_block(parent))
    self_usage = dict(usage.get("self") or {})
    wall = self_usage.get("duration")

    child_durations = [
        _inclusive_usage(child).get("duration") for child in children
    ]
    known_child_durations = [d for d in child_durations if d is not None]
    child_wall = sum(known_child_durations) if known_child_durations else 0.0
    if wall is not None:
        self_usage["duration"] = max(0.0, float(wall) - float(child_wall))

    def _roll(key: str):
        values: list = []
        own = self_usage.get(key)
        if own is not None:
            values.append(own)
        for child in children:
            value = _inclusive_usage(child).get(key)
            if value is not None:
                values.append(value)
        return sum(values) if values else None

    return {
        **parent,
        "usage": {
            "self": self_usage,
            "total": _usage_bag(
                input_tokens=_roll("input_tokens"),
                output_tokens=_roll("output_tokens"),
                duration=wall,
                cost=_roll("cost"),
            ),
        },
        "steps": children,
    }


def flatten_step_metrics(steps: list[dict]) -> list[dict]:
    """Flatten nested step metrics into a list of per-call ``usage.self`` bags."""
    flat: list[dict] = []
    for node in steps:
        if not isinstance(node, dict):
            continue
        children = node.get("steps")
        if not isinstance(children, list):
            children = []
        own = _usage_block(node).get("self")
        if not isinstance(own, dict):
            own = {}
        flat.append({"agent": node.get("agent"), **own})
        if children:
            flat.extend(flatten_step_metrics(children))
    return flat


def summarize_step_metrics(steps: list[dict]) -> dict:
    """Roll up per-step ``usage.self`` bags into run-level provider_usage fields.

    Cost, tokens, and exclusive duration are summed over every node's own call.
    Providers is the sorted unique set of non-empty provider names. Wall-clock
    end-to-end time remains run-level ``duration_seconds`` (may exceed the
    summed exclusive step durations when there are gaps between steps).
    """
    flat = flatten_step_metrics(steps)
    costs = [step["cost"] for step in flat if step.get("cost") is not None]
    input_tokens = [
        step["input_tokens"] for step in flat if step.get("input_tokens") is not None
    ]
    output_tokens = [
        step["output_tokens"] for step in flat if step.get("output_tokens") is not None
    ]
    durations = [
        step["duration"] for step in flat if step.get("duration") is not None
    ]
    providers = sorted(
        {
            str(step["provider"])
            for step in flat
            if step.get("provider") not in (None, "")
        }
    )
    return {
        "cost": sum(costs) if costs else None,
        "input_tokens": sum(input_tokens) if input_tokens else None,
        "output_tokens": sum(output_tokens) if output_tokens else None,
        "duration": sum(durations) if durations else None,
        "providers": providers,
        "n_calls": len(flat),
    }


def _add_optional_number(
    base: float | int | None,
    extra: float | int | None,
    *,
    cast: type,
) -> float | int | None:
    """Return ``base + extra`` when either side is present; else ``None``."""
    if extra is None:
        return base
    if base is None:
        return cast(extra)
    return cast(base) + cast(extra)


def merge_activity_summary_into_provider_usage(
    provider_usage: dict,
    summary_metrics: dict | None,
) -> dict:
    """Return a copy of *provider_usage* with activity-summary usage folded in.

    Step rollups stay authoritative for ``duration`` (exclusive step time).
    Cost, tokens, providers, and ``n_calls`` include summarisation LLM calls
    so run-level totals cover the full pipeline including ``activity.md``.
    """
    merged = dict(provider_usage or {})
    summary = summary_metrics if isinstance(summary_metrics, dict) else {}
    if not summary:
        return merged

    merged["cost"] = _add_optional_number(
        merged.get("cost"), summary.get("cost"), cast=float
    )
    for token_key in ("input_tokens", "output_tokens"):
        merged[token_key] = _add_optional_number(
            merged.get(token_key), summary.get(token_key), cast=int
        )

    providers = list(merged.get("providers") or [])
    for provider in summary.get("providers") or []:
        if provider and provider not in providers:
            providers.append(str(provider))
    if providers:
        merged["providers"] = sorted(providers)

    n_summary_calls = int(summary.get("n_calls") or 0)
    if n_summary_calls:
        merged["n_calls"] = _add_optional_number(
            merged.get("n_calls"), n_summary_calls, cast=int
        )
    return merged


def activity_summary_payload(
    *,
    skipped: bool,
    summary_metrics: dict | None,
) -> dict:
    """Build the ``activity_summary`` object written to ``run.json``."""
    metrics = summary_metrics if isinstance(summary_metrics, dict) else {}
    return {"skipped": skipped, **metrics}


AGENT_ROLES: dict[str, str] = {
    "orchestrator": "Coordinates the systematic review pipeline, delegating tasks to specialised agents",
    "librarian": "Searches for and retrieves candidate studies from the literature database",
    "gatekeeper": "Screens candidate studies for inclusion or exclusion based on the review criteria",
    "miner": "Extracts structured evidence (PICO, outcomes, effect measures) from included studies",
    "critic": "Synthesises the extracted evidence and assesses its quality",
}

MAX_MODEL_OUTPUT_CHARS = 4000
MAX_OBSERVATIONS_CHARS = 2000
MAX_PLAN_CHARS = 3000
MAX_OUTPUT_CHARS = 2000


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
    cost: float | None = None
    provider: str | None = None

    def to_metrics(self) -> dict:
        """Return operational fields for run.json (leaf: ``usage.self`` only)."""
        return {
            "agent": self.agent_name,
            "step_type": self.step_type,
            "step_number": self.step_number,
            "usage": {
                "self": _usage_bag(
                    input_tokens=self.token_input,
                    output_tokens=self.token_output,
                    duration=self.duration_seconds,
                    cost=self.cost,
                    provider=self.provider,
                    include_provider=True,
                ),
            },
        }


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
        # Populated by ``finalize`` (LLM activity.md summarisation calls).
        self.summary_metrics: dict = {
            "n_calls": 0,
            "duration": 0.0,
            "cost": None,
            "input_tokens": None,
            "output_tokens": None,
            "providers": [],
        }

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
        agent_name = get_agent_name(agent)
        duration = step.timing.duration if step.timing else None
        usage = extract_call_usage(raw_completion_from_step(step))

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
            cost=usage["cost"],
            provider=usage["provider"],
            tool_calls=tool_names,
            model_output=model_out,
            code_action=step.code_action,
            observations=(
                str(step.observations) if step.observations else None
            ),
            action_output=(
                str(step.action_output)[:MAX_OUTPUT_CHARS]
                if step.action_output else None
            ),
            is_final_answer=step.is_final_answer,
            error=str(step.error) if step.error else None,
        ))

    def record_planning_step(self, step: PlanningStep, agent=None) -> None:
        """Record a PlanningStep from a smolagents callback."""
        agent_name = get_agent_name(agent)
        duration = step.timing.duration if step.timing else None
        usage = extract_call_usage(raw_completion_from_step(step))

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
            cost=usage["cost"],
            provider=usage["provider"],
        ))

    def step_metrics(self) -> list[dict]:
        """Serialize agent steps with delegated work nested under its parent."""
        steps: list[dict] = []
        for phase in self._group_into_phases():
            children = [step.to_metrics() for step in phase.subagent_steps]
            if phase.orchestrator_step is None:
                steps.extend(children)
            else:
                parent = phase.orchestrator_step.to_metrics()
                if children:
                    parent = with_nested_steps(parent, children)
                steps.append(parent)
        return steps

    def finalize(self, model=None) -> Path:
        """Summarise every step with the LLM and write ``activity.md``.

        Args:
            model: The smolagents model to use for summarisation.
                   If *None*, a template-based fallback is used.

        Returns:
            Path to the written ``activity.md`` file.

        Side effect:
            Updates ``self.summary_metrics`` with wall time / usage for any
            LLM summarisation calls (zeros / nulls when *model* is None).
        """
        self.mark_pipeline_end()
        started = time.perf_counter()
        costs: list[float] = []
        input_tokens: list[int] = []
        output_tokens: list[int] = []
        providers: set[str] = set()
        n_calls = 0

        for step in self.steps:
            # Skip sub-agent summarisation when they won't be shown
            if not self.include_subagent_steps and step.agent_name != "orchestrator":
                continue
            if model is not None:
                try:
                    step.summary, call_usage = self._summarize_step(step, model)
                    n_calls += 1
                    if call_usage.get("cost") is not None:
                        costs.append(float(call_usage["cost"]))
                    if call_usage.get("input_tokens") is not None:
                        input_tokens.append(int(call_usage["input_tokens"]))
                    if call_usage.get("output_tokens") is not None:
                        output_tokens.append(int(call_usage["output_tokens"]))
                    if call_usage.get("provider"):
                        providers.add(str(call_usage["provider"]))
                except Exception:
                    step.summary = self._fallback_summary(step)
            else:
                step.summary = self._fallback_summary(step)

        self.summary_metrics = {
            "n_calls": n_calls,
            "duration": time.perf_counter() - started,
            "cost": sum(costs) if costs else None,
            "input_tokens": sum(input_tokens) if input_tokens else None,
            "output_tokens": sum(output_tokens) if output_tokens else None,
            "providers": sorted(providers),
        }

        output_path = self.run_dir / "activity.md"
        output_path.write_text(self._build_markdown(), encoding="utf-8")
        return output_path

    # -- LLM summarisation --------------------------------------------------

    def _summarize_step(self, step: StepRecord, model) -> tuple[str, dict]:
        """Call the LLM with a short prompt to summarise one step.

        Returns:
            ``(summary_text, usage_dict)`` where usage has cost / tokens /
            provider when the provider surfaces them on the raw response.
        """
        from smolagents.models import ChatMessage, MessageRole

        role_desc = AGENT_ROLES.get(
            step.agent_name,
            "Agent in the systematic review pipeline",
        )

        if step.step_type == "planning":
            context = (
                    "--- Plan ---\n"
                    + truncate(step.plan_text, MAX_PLAN_CHARS)
            )
            activity = "Planning the next steps"
        else:
            parts: list[str] = []
            if step.model_output:
                parts.append(
                    "--- Agent reasoning and actions ---\n"
                    + truncate(step.model_output, MAX_MODEL_OUTPUT_CHARS)
                )
            if step.observations:
                parts.append(
                    "--- Execution result ---\n"
                    + truncate(step.observations, MAX_OBSERVATIONS_CHARS)
                )
            if step.error:
                parts.append(f"--- Error ---\n{str(step.error)[:500]}")
            if step.is_final_answer and step.action_output:
                parts.append(
                    "--- Final output ---\n"
                    + truncate(step.action_output, MAX_OUTPUT_CHARS)
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
        usage = extract_call_usage(getattr(response, "raw", None))
        token_usage = getattr(response, "token_usage", None)
        if token_usage is not None:
            usage["input_tokens"] = getattr(token_usage, "input_tokens", None)
            usage["output_tokens"] = getattr(token_usage, "output_tokens", None)
        else:
            raw_usage = getattr(getattr(response, "raw", None), "usage", None)
            if isinstance(raw_usage, dict):
                usage["input_tokens"] = raw_usage.get("prompt_tokens") or raw_usage.get(
                    "input_tokens"
                )
                usage["output_tokens"] = raw_usage.get(
                    "completion_tokens"
                ) or raw_usage.get("output_tokens")
            else:
                usage["input_tokens"] = getattr(raw_usage, "prompt_tokens", None) or getattr(
                    raw_usage, "input_tokens", None
                )
                usage["output_tokens"] = getattr(
                    raw_usage, "completion_tokens", None
                ) or getattr(raw_usage, "output_tokens", None)

        # Extract plain text from the response
        if isinstance(response.content, str):
            text = response.content.strip()
        elif isinstance(response.content, list):
            text = " ".join(
                item.get("text", "")
                for item in response.content
                if isinstance(item, dict)
            ).strip()
        else:
            text = str(response.content).strip()
        return text, usage

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
            lines.append(f"> **Duration:** {format_duration(dur)}  ")

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
                d = format_duration(s["dur"]) if s["dur"] else "—"
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
                f"| **Total** | **{tot_n}** | **{format_duration(tot_d)}** "
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
                meta.append(format_duration(orch.duration_seconds))
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
        """Compute per-agent aggregates using exclusive (self) durations."""
        stats: dict[str, dict] = {}

        def _bump(agent: str, *, duration: float, token_in: int, token_out: int) -> None:
            if agent not in stats:
                stats[agent] = {"n": 0, "dur": 0.0, "in": 0, "out": 0}
            st = stats[agent]
            st["n"] += 1
            st["dur"] += duration
            st["in"] += token_in
            st["out"] += token_out

        for phase in self._group_into_phases():
            children = phase.subagent_steps
            child_wall = sum(s.duration_seconds or 0.0 for s in children)
            orch = phase.orchestrator_step
            if orch is not None:
                wall = orch.duration_seconds or 0.0
                exclusive = max(0.0, wall - child_wall) if children else wall
                _bump(
                    orch.agent_name,
                    duration=exclusive,
                    token_in=orch.token_input or 0,
                    token_out=orch.token_output or 0,
                )
            for step in children:
                _bump(
                    step.agent_name,
                    duration=step.duration_seconds or 0.0,
                    token_in=step.token_input or 0,
                    token_out=step.token_output or 0,
                )
        return stats


