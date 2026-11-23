"""Tests for systematic review and protocol JSON serialization helpers."""

import json
from types import SimpleNamespace

import pytest

from mentor.review import (
    Criterion,
    SelectionCriteria,
    normalize_mode,
    parse_selection_criteria,
    review_from_dict,
)
from mentor.runtime.session import protocol_to_json, review_to_json

_SAMPLE_CRITERIA = SelectionCriteria(
    inclusion=[Criterion(id="IC1", text="Include RCTs")],
    exclusion=[Criterion(id="EC1", text="Exclude narrative reviews")],
)
_SAMPLE_CRITERIA_DICT = _SAMPLE_CRITERIA.to_dict()


def test_review_to_json_includes_mode_and_studies():
    review = SimpleNamespace(
        mode="screening-only",
        title="T",
        objective="O",
        background="B",
        selection_criteria=_SAMPLE_CRITERIA,
        studies=[
            SimpleNamespace(title="s1", abstract="a1"),
            SimpleNamespace(title="s2", abstract="a2"),
        ],
    )
    payload = json.loads(review_to_json(review))
    assert payload["mode"] == "screening-only"
    assert payload["selection_criteria"] == _SAMPLE_CRITERIA_DICT
    assert "n_total" not in payload
    assert "review_url" not in payload
    assert len(payload["studies"]) == 2
    assert payload["studies"][0]["study_index"] == 1


def test_review_to_json_omits_studies_for_full_mode():
    review = SimpleNamespace(
        mode="full",
        title="T",
        objective="O",
        background="B",
        selection_criteria=_SAMPLE_CRITERIA,
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
        selection_criteria=_SAMPLE_CRITERIA,
        studies=[SimpleNamespace(title="s1", abstract="a1")],
    )
    payload = json.loads(protocol_to_json(review))
    assert "studies" not in payload
    assert payload["title"] == "T"
    assert payload["selection_criteria"] == _SAMPLE_CRITERIA_DICT


def test_screening_only_mode_requires_studies():
    with pytest.raises(ValueError, match="mode=screening-only requires"):
        review_from_dict(
            {
                "mode": "screening-only",
                "title": "T",
                "objective": "O",
                "background": "B",
                "selection_criteria": _SAMPLE_CRITERIA_DICT,
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
                "selection_criteria": _SAMPLE_CRITERIA_DICT,
                "studies": [{"title": "s1", "abstract": "a1"}],
            }
        )


def test_omitted_mode_defaults_to_full():
    review = review_from_dict(
        {
            "title": "T",
            "objective": "O",
            "background": "B",
            "selection_criteria": _SAMPLE_CRITERIA_DICT,
        }
    )
    assert review.mode == "full"
    assert review.studies == []
    assert review.selection_criteria.to_dict() == _SAMPLE_CRITERIA_DICT


def test_omitted_mode_with_studies_is_rejected():
    with pytest.raises(ValueError, match="mode=full expects protocol-only"):
        review_from_dict(
            {
                "title": "T",
                "objective": "O",
                "background": "B",
                "selection_criteria": _SAMPLE_CRITERIA_DICT,
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
            "selection_criteria": _SAMPLE_CRITERIA_DICT,
            "studies": [{"title": "s1", "abstract": "a1"}],
        }
    )
    assert review.mode == "screening-only"
    assert len(review.studies) == 1
    assert review.studies[0].metadata == {}


def test_study_metadata_round_trips_through_review_json():
    review = review_from_dict(
        {
            "mode": "screening-only",
            "title": "T",
            "objective": "O",
            "background": "B",
            "selection_criteria": _SAMPLE_CRITERIA_DICT,
            "studies": [
                {
                    "title": "s1",
                    "abstract": "a1",
                    "journal": "Lancet",
                    "publication_year": 2004,
                    "publication_types": ["Journal Article", "RCT"],
                }
            ],
        }
    )
    study = review.studies[0]
    assert study.metadata == {
        "journal": "Lancet",
        "publication_year": 2004,
        "publication_types": ["Journal Article", "RCT"],
    }

    payload = json.loads(review_to_json(review))
    record = payload["studies"][0]
    assert record["study_index"] == 1
    assert record["title"] == "s1"
    assert record["abstract"] == "a1"
    assert record["journal"] == "Lancet"
    assert record["publication_year"] == 2004
    assert record["publication_types"] == ["Journal Article", "RCT"]
    assert "metadata" not in record


def test_study_label_key_is_ignored():
    review = review_from_dict(
        {
            "mode": "screening-only",
            "title": "T",
            "objective": "O",
            "background": "B",
            "selection_criteria": _SAMPLE_CRITERIA_DICT,
            "studies": [
                {
                    "title": "s1",
                    "abstract": "a1",
                    "label": 1.0,
                    "journal": "BMJ",
                }
            ],
        }
    )
    assert review.studies[0].metadata == {"journal": "BMJ"}
    assert "label" not in json.loads(review_to_json(review))["studies"][0]


def test_parse_selection_criteria_rejects_free_text():
    with pytest.raises(ValueError, match="free-text strings are not accepted"):
        parse_selection_criteria("Include RCTs")


def test_parse_selection_criteria_rejects_wrong_id_prefix():
    with pytest.raises(ValueError, match="must match IC"):
        parse_selection_criteria(
            {
                "inclusion": [{"id": "EC1", "text": "wrong bucket"}],
                "exclusion": [{"id": "EC2", "text": "ok"}],
            }
        )


def test_parse_selection_criteria_normalizes_ids():
    parsed = parse_selection_criteria(
        {
            "inclusion": [{"id": "ic1", "text": "Adults"}],
            "exclusion": [{"id": "ec1", "text": "Reviews"}],
        }
    )
    assert parsed.criterion_ids() == ["IC1", "EC1"]
    assert "Inclusion criteria:" in parsed.format_text()


def test_parse_selection_criteria_allows_missing_exclusion():
    parsed = parse_selection_criteria(
        {"inclusion": [{"id": "IC1", "text": "Adults"}]}
    )
    assert parsed.criterion_ids() == ["IC1"]
    assert parsed.exclusion == []
    assert "Exclusion criteria:" not in parsed.format_text()


def test_parse_selection_criteria_allows_empty_inclusion():
    parsed = parse_selection_criteria(
        {
            "inclusion": [],
            "exclusion": [{"id": "EC1", "text": "Reviews"}],
        }
    )
    assert parsed.criterion_ids() == ["EC1"]
    assert parsed.inclusion == []


def test_parse_selection_criteria_rejects_both_empty():
    with pytest.raises(ValueError, match="at least one"):
        parse_selection_criteria({"inclusion": [], "exclusion": []})
