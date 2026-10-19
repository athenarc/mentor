"""
Experiment-only agent instruction prompts (screening batch/loop variants).

Load via ``load_prompt``; filenames mirror roles such as batch vs loop
gatekeeper/orchestrator. Uses ``importlib.resources`` so prompts resolve from
the installed ``experiments.prompts`` package.
"""

from __future__ import annotations

from importlib.resources import files


def load_prompt(name: str) -> str:
    """Return the contents of ``experiments/prompts/<name>.md``."""
    return files("experiments.prompts").joinpath(f"{name}.md").read_text(encoding="utf-8")


__all__ = ["load_prompt"]
