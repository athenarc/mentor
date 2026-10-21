"""
Production system prompts for Mentor agents.

Markdown files live alongside this package; load them with ``load_prompt(name)``
to obtain the orchestrator/librarian/gatekeeper/miner/critic instructions.
Uses ``importlib.resources`` so prompts resolve from the installed package.

Per-run overrides: pass a ``prompt_paths`` map (role → file path) to
``resolve_prompt``; missing keys fall back to the packaged default.

Review JSON ``prompts`` uses a single ``orchestrator`` key for both modes;
the packaged default file still depends on mode (``orchestrator.md`` vs
``orchestrator_screening-only.md``).
"""

from __future__ import annotations

from importlib.resources import files
from pathlib import Path
from typing import Mapping

# Roles that may appear under review JSON ``prompts``.
PROMPT_ROLES = frozenset(
    {
        "orchestrator",
        "librarian",
        "gatekeeper",
        "miner",
        "critic",
    }
)


def load_prompt(name: str) -> str:
    """Return the contents of ``mentor/agents/prompts/<name>.md``."""
    return files("mentor.agents.prompts").joinpath(f"{name}.md").read_text(
        encoding="utf-8"
    )


def resolve_prompt(
    name: str,
    prompt_paths: Mapping[str, str | Path] | None = None,
    *,
    default: str | None = None,
) -> str:
    """Load a prompt from ``prompt_paths[name]`` if set, else the packaged default.

    ``default`` is the packaged prompt stem when it differs from ``name``
    (e.g. override key ``orchestrator`` with default
    ``orchestrator_screening-only``).
    """
    if prompt_paths and name in prompt_paths:
        path = Path(prompt_paths[name])
        if not path.is_file():
            raise ValueError(f"Prompt override for '{name}' not found: {path}")
        return path.read_text(encoding="utf-8")
    return load_prompt(default or name)


__all__ = ["PROMPT_ROLES", "load_prompt", "resolve_prompt"]
