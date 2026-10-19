"""
Production system prompts for Mentor agents.

Markdown files live alongside this package; load them with ``load_prompt(name)``
to obtain the orchestrator/librarian/gatekeeper/miner/critic instructions.
Uses ``importlib.resources`` so prompts resolve from the installed package.
"""

from __future__ import annotations

from importlib.resources import files


def load_prompt(name: str) -> str:
    """Return the contents of ``mentor/agents/prompts/<name>.md``."""
    return files("mentor.agents.prompts").joinpath(f"{name}.md").read_text(
        encoding="utf-8"
    )


__all__ = ["load_prompt"]
