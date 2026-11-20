"""Prompt package-resource loading checks."""

from __future__ import annotations

from importlib.resources import files
from pathlib import Path

import pytest

from mentor.agents.prompts import load_prompt as load_prod_prompt
from mentor.agents.prompts import resolve_prompt
from mentor.review import review_from_dict

_SAMPLE_CRITERIA = {
    "inclusion": [{"id": "IC1", "text": "Include RCTs"}],
    "exclusion": [{"id": "EC1", "text": "Exclude reviews"}],
}

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
    assert "additional_args['screening_payload']" in text
    assert "study_index" in text
    assert "get_final_decision" in text
    assert "format_screening_tasks" in text
    assert "final_answer(json.dumps(" in text
    assert "Include every study in the batch exactly once" in text


def test_orchestrator_uses_managed_gatekeeper_batches() -> None:
    text = load_prod_prompt("orchestrator")
    assert "get_screening_batches" in text
    assert "append_screening_batch" in text
    assert "gatekeeper(" in text
    assert "INCLUDE | EXCLUDE | UNCLEAR" in text
    assert "INCLUDE and UNCLEAR" in text
    assert "ContextOverflowError" in text
    assert "except Exception:" in text
    assert "type(exc).__name__" not in text
    assert "screen_candidates" not in text
    screening_only = load_prod_prompt("orchestrator_screening-only")
    assert "get_screening_batches" in screening_only
    assert "append_screening_batch" in screening_only
    assert "format_screening_progress_summary" in screening_only
    assert "gatekeeper" in screening_only
    assert "ContextOverflowError" in screening_only
    assert "except Exception:" in screening_only
    assert "type(exc).__name__" not in screening_only
    assert "screen_candidates" not in screening_only
    assert "get_screening_response_json" not in screening_only


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
            "selection_criteria": _SAMPLE_CRITERIA,
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
                "selection_criteria": _SAMPLE_CRITERIA,
                "prompts": {"unknown_agent": "x.md"},
            }
        )
