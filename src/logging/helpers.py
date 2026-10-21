"""Shared logging helpers."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from mentor.settings import OUTPUT_DIR


def make_run_dir(review_title: str, output_root: Path | None = None) -> Path:
    """Create a timestamped output directory for this run."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_title = "".join(
        c if c.isalnum() or c in " -_" else "" for c in review_title
    )[:60].strip()
    root = output_root or OUTPUT_DIR
    run_dir = root / f"{timestamp}_{safe_title}"
    run_dir.mkdir(parents=True, exist_ok=True)
    return run_dir


def get_agent_name(agent) -> str:
    """Extract a readable name from a smolagents agent object."""
    if agent and hasattr(agent, "name") and agent.name:
        return agent.name
    return "orchestrator"


def truncate(text: str | None, limit: int) -> str:
    """Return *text* clipped to *limit* characters."""
    if not text:
        return ""
    if len(text) <= limit:
        return text
    return text[:limit] + "\n… [truncated]"


def format_duration(seconds: float) -> str:
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
