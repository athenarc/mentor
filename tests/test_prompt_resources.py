"""Prompt package-resource loading checks."""

from __future__ import annotations

from importlib.resources import files
from pathlib import Path

import pytest

from mentor.agents.prompts import load_prompt as load_prod_prompt
from mentor.agents.prompts import resolve_prompt
from mentor.review import review_from_dict

PROD = [
    "orchestrator",
    "orchestrator_screening-only",  # packaged default for mode=screening-only
    "librarian",
    "gatekeeper",
    "miner",
    "critic",
]


@pytest.mark.parametrize("name", PROD)
def test_production_prompts_load(name: str) -> None:
    text = load_prod_prompt(name)
    assert isinstance(text, str) and len(text) > 50
    packaged = files("mentor.agents.prompts").joinpath(f"{name}.md").read_text(
        encoding="utf-8"
    )
    assert text == packaged


def test_gatekeeper_prompt_is_batch_agnostic() -> None:
    text = load_prod_prompt("gatekeeper")
    assert "Preserve the original study_index" in text
    assert "Do NOT include decisions for studies outside the payload" in text


def test_orchestrator_uses_screen_candidates() -> None:
    text = load_prod_prompt("orchestrator")
    assert "screen_candidates" in text
    assert "gatekeeper(task=" not in text


def test_resolve_prompt_override(tmp_path: Path) -> None:
    custom = tmp_path / "gatekeeper.md"
    custom.write_text("CUSTOM GATEKEEPER PROMPT", encoding="utf-8")
    assert resolve_prompt("gatekeeper", {"gatekeeper": custom}) == "CUSTOM GATEKEEPER PROMPT"
    assert resolve_prompt("librarian", {"gatekeeper": custom}) == load_prod_prompt("librarian")


def test_orchestrator_override_key_uses_mode_default_file(tmp_path: Path) -> None:
    custom = tmp_path / "orch.md"
    custom.write_text("CUSTOM ORCH", encoding="utf-8")
    assert (
        resolve_prompt("orchestrator", {"orchestrator": custom}) == "CUSTOM ORCH"
    )
    # No override → screening-only packaged default when default= is set.
    assert (
        resolve_prompt("orchestrator", default="orchestrator_screening-only")
        == load_prod_prompt("orchestrator_screening-only")
    )


def test_review_prompts_resolve_relative_to_review_file(tmp_path: Path) -> None:
    prompt = tmp_path / "custom_gk.md"
    prompt.write_text("override", encoding="utf-8")
    review = review_from_dict(
        {
            "mode": "screening-only",
            "title": "T",
            "objective": "O",
            "background": "B",
            "selection_criteria": "S",
            "prompts": {"gatekeeper": "custom_gk.md"},
            "studies": [{"title": "s1", "abstract": "a1"}],
        },
        base_dir=tmp_path,
    )
    assert review.prompts["gatekeeper"] == str(prompt.resolve())


def test_review_prompts_reject_unknown_role() -> None:
    with pytest.raises(ValueError, match="Unknown prompt role"):
        review_from_dict(
            {
                "mode": "full",
                "title": "T",
                "objective": "O",
                "background": "B",
                "selection_criteria": "S",
                "prompts": {"unknown_agent": "x.md"},
            }
        )
