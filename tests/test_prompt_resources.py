"""Prompt package-resource loading and parity checks."""

from __future__ import annotations

from importlib.resources import files

import pytest

from experiments.prompts import load_prompt as load_exp_prompt
from mentor.agents.prompts import load_prompt as load_prod_prompt

PROD = ["orchestrator", "librarian", "gatekeeper", "miner", "critic"]
EXP = [
    "screening_orchestrator",
    "screening_loop_orchestrator",
    "screening_chunk_loop_orchestrator",
    "gatekeeper_single",
    "gatekeeper_chunk",
]


@pytest.mark.parametrize("name", PROD)
def test_production_prompts_load(name: str) -> None:
    text = load_prod_prompt(name)
    assert isinstance(text, str) and len(text) > 50
    packaged = files("mentor.agents.prompts").joinpath(f"{name}.md").read_text(
        encoding="utf-8"
    )
    assert text == packaged


@pytest.mark.parametrize("name", EXP)
def test_experiment_prompts_load(name: str) -> None:
    text = load_exp_prompt(name)
    assert isinstance(text, str) and len(text) > 50
    packaged = files("experiments.prompts").joinpath(f"{name}.md").read_text(encoding="utf-8")
    assert text == packaged
