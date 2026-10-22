"""Tests for systematic review and protocol JSON serialization helpers."""

import json
from types import SimpleNamespace

import pytest

from mentor.review import normalize_mode, review_from_dict
from mentor.runtime.session import protocol_to_json, review_to_json


def test_review_to_json_includes_mode_and_studies_without_labels():
    review = SimpleNamespace(
        mode="screening-only",
        title="T",
        objective="O",
        background="B",
        selection_criteria="S",
        studies=[
            SimpleNamespace(title="s1", abstract="a1"),
            SimpleNamespace(title="s2", abstract="a2"),
        ],
    )
    payload = json.loads(review_to_json(review))
    assert payload["mode"] == "screening-only"
    assert "n_total" not in payload
    assert "review_url" not in payload
    assert len(payload["studies"]) == 2
    assert payload["studies"][0]["study_index"] == 1
    assert "label" not in payload["studies"][0]


def test_review_to_json_omits_studies_for_full_mode():
    review = SimpleNamespace(
        mode="full",
        title="T",
        objective="O",
        background="B",
        selection_criteria="S",
        studies=[],
    )
    payload = json.loads(review_to_json(review))
    assert payload["mode"] == "full"
    assert "studies" not in payload


def test_protocol_to_json_excludes_studies():
    review = SimpleNamespace(
        title="T",
        objective="O",
        background="B",
        selection_criteria="S",
        studies=[SimpleNamespace(title="s1", abstract="a1")],
    )
    payload = json.loads(protocol_to_json(review))
    assert "studies" not in payload
    assert payload["title"] == "T"


def test_screening_only_mode_requires_studies():
    with pytest.raises(ValueError, match="mode=screening-only requires"):
        review_from_dict(
            {
                "mode": "screening-only",
                "title": "T",
                "objective": "O",
                "background": "B",
                "selection_criteria": "S",
            }
        )


def test_full_mode_rejects_studies():
    with pytest.raises(ValueError, match="mode=full expects protocol-only"):
        review_from_dict(
            {
                "mode": "full",
                "title": "T",
                "objective": "O",
                "background": "B",
                "selection_criteria": "S",
                "studies": [{"title": "s1", "abstract": "a1"}],
            }
        )


def test_omitted_mode_defaults_to_full():
    review = review_from_dict(
        {
            "title": "T",
            "objective": "O",
            "background": "B",
            "selection_criteria": "S",
        }
    )
    assert review.mode == "full"
    assert review.studies == []


def test_omitted_mode_with_studies_is_rejected():
    with pytest.raises(ValueError, match="mode=full expects protocol-only"):
        review_from_dict(
            {
                "title": "T",
                "objective": "O",
                "background": "B",
                "selection_criteria": "S",
                "studies": [{"title": "s1", "abstract": "a1"}],
            }
        )


def test_screening_mode_alias_rejected():
    with pytest.raises(ValueError, match="mode"):
        normalize_mode("screening")


def test_screening_only_mode_loads_studies():
    review = review_from_dict(
        {
            "mode": "screening-only",
            "title": "T",
            "objective": "O",
            "background": "B",
            "selection_criteria": "S",
            "studies": [{"title": "s1", "abstract": "a1"}],
        }
    )
    assert review.mode == "screening-only"
    assert len(review.studies) == 1
