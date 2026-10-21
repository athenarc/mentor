"""
Telemetry helpers for screening benchmark runs.

The benchmark metrics focus on screening quality.  This module adds the
workflow and rationale-quality measurements that are useful for comparing
agentic reliability and operational burden across benchmark architectures.
"""

from __future__ import annotations

from collections import Counter
from typing import Any


def _normalize_reason(value: Any) -> str:
    text = str(value or "").strip()
    return " ".join(text.lower().split())


def collect_activity_telemetry(
    activity_logger,
    *,
    duration_seconds: float,
    n_studies: int,
    retry_count: int = 0,
    resume_count: int = 0,
) -> dict:
    """
    Build machine-readable run telemetry from an ActivityLogger instance.

    Args:
        activity_logger: The logger populated by smolagents step callbacks.
        duration_seconds: End-to-end run duration.
        n_studies: Number of studies in the review.
        retry_count: Number of benchmark-level reruns after the first attempt.
        resume_count: Number of attempts that resumed from persisted decisions.

    Returns:
        Flat scalar fields plus small per-agent dictionaries for JSON summaries.
    """
    steps = list(getattr(activity_logger, "steps", []) or [])
    per_agent_steps: Counter[str] = Counter()
    per_agent_input_tokens: Counter[str] = Counter()
    per_agent_output_tokens: Counter[str] = Counter()
    per_agent_duration: Counter[str] = Counter()
    total_input_tokens = 0
    total_output_tokens = 0
    error_step_count = 0
    planning_step_count = 0
    action_step_count = 0

    for step in steps:
        agent_name = str(getattr(step, "agent_name", "") or "unknown")
        per_agent_steps[agent_name] += 1
        token_input = int(getattr(step, "token_input", None) or 0)
        token_output = int(getattr(step, "token_output", None) or 0)
        total_input_tokens += token_input
        total_output_tokens += token_output
        per_agent_input_tokens[agent_name] += token_input
        per_agent_output_tokens[agent_name] += token_output
        per_agent_duration[agent_name] += float(getattr(step, "duration_seconds", None) or 0.0)
        if getattr(step, "error", None):
            error_step_count += 1
        step_type = str(getattr(step, "step_type", "") or "")
        if step_type == "planning":
            planning_step_count += 1
        elif step_type == "action":
            action_step_count += 1

    total_tokens = total_input_tokens + total_output_tokens
    return {
        "total_input_tokens": total_input_tokens,
        "total_output_tokens": total_output_tokens,
        "total_tokens": total_tokens,
        "total_steps": len(steps),
        "action_step_count": action_step_count,
        "planning_step_count": planning_step_count,
        "error_step_count": error_step_count,
        "retry_count": int(retry_count),
        "resume_count": int(resume_count),
        "duration_per_study_seconds": (
            duration_seconds / n_studies if n_studies else None
        ),
        "agent_step_counts": dict(per_agent_steps),
        "agent_input_tokens": dict(per_agent_input_tokens),
        "agent_output_tokens": dict(per_agent_output_tokens),
        "agent_duration_seconds": dict(per_agent_duration),
        "orchestrator_step_count": per_agent_steps.get("orchestrator", 0),
        "gatekeeper_step_count": per_agent_steps.get("gatekeeper", 0),
        "orchestrator_input_tokens": per_agent_input_tokens.get("orchestrator", 0),
        "orchestrator_output_tokens": per_agent_output_tokens.get("orchestrator", 0),
        "gatekeeper_input_tokens": per_agent_input_tokens.get("gatekeeper", 0),
        "gatekeeper_output_tokens": per_agent_output_tokens.get("gatekeeper", 0),
    }


def compute_rationale_metrics(screening_decisions: list[dict]) -> dict:
    """
    Compute rationale-quality counters from normalized screening decisions.

    The parser canonicalizes both ``reason`` and ``rationale`` into ``reason``.
    Empty and repeated rationales are useful indicators of shortcut behavior.
    """
    normalized_reasons = [
        _normalize_reason(
            decision.get("reason", decision.get("rationale", ""))
        )
        for decision in screening_decisions
    ]
    empty_count = sum(1 for reason in normalized_reasons if not reason)
    non_empty = [reason for reason in normalized_reasons if reason]
    counts = Counter(non_empty)
    duplicate_count = sum(count - 1 for count in counts.values() if count > 1)
    total = len(screening_decisions)
    return {
        "empty_rationale_count": empty_count,
        "duplicate_rationale_count": duplicate_count,
        "unique_rationale_count": len(counts),
        "rationale_reuse_rate": duplicate_count / total if total else None,
    }
