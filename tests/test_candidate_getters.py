"""Batch payload helper: single index equals batch of size one."""

from __future__ import annotations

import json

from mentor.tools.search.search_tools import (
    _candidate_studies_batch_payload,
    load_review_data,
)
from mentor.tools.screening_tools import format_screening_tasks

_SAMPLE_CRITERIA = {
    "inclusion": [{"id": "IC1", "text": "Include RCTs"}],
    "exclusion": [{"id": "EC1", "text": "Exclude reviews"}],
}


def test_single_index_matches_batch_size_one():
    payload = {
        "title": "T",
        "objective": "O",
        "background": "B",
        "selection_criteria": _SAMPLE_CRITERIA,
        "studies": [
            {"study_index": 1, "title": "s1", "abstract": "a1"},
            {"study_index": 2, "title": "s2", "abstract": "a2"},
        ],
    }
    load_review_data(json.dumps(payload))
    single = _candidate_studies_batch_payload("[2]")
    same = _candidate_studies_batch_payload("[2]")
    assert json.loads(single) == json.loads(same)
    assert len(json.loads(single)["studies"]) == 1
    assert json.loads(single)["studies"][0]["study_index"] == 2


def test_batch_payload_preserves_extra_study_metadata():
    payload = {
        "title": "T",
        "objective": "O",
        "background": "B",
        "selection_criteria": _SAMPLE_CRITERIA,
        "studies": [
            {
                "study_index": 1,
                "title": "s1",
                "abstract": "a1",
                "journal": "Lancet",
                "publication_date": "2020-01-01",
                "publication_types": ["Journal Article", "RCT"],
            },
        ],
    }
    load_review_data(json.dumps(payload))
    study = json.loads(_candidate_studies_batch_payload("[1]"))["studies"][0]
    assert study["journal"] == "Lancet"
    assert study["publication_date"] == "2020-01-01"
    assert study["publication_types"] == ["Journal Article", "RCT"]


def test_format_screening_tasks_includes_extra_metadata_and_checklist():
    text = format_screening_tasks(
        json.dumps(
            {
                "title": "Review",
                "selection_criteria": _SAMPLE_CRITERIA,
                "studies": [
                    {
                        "study_index": 1,
                        "title": "s1",
                        "abstract": "a1",
                        "journal": "BMJ",
                        "year": 2019,
                    }
                ],
            }
        )
    )
    assert "Title: s1" in text
    assert "Abstract: a1" in text
    assert "journal: BMJ" in text
    assert "year: 2019" in text
    assert "- IC1: Include RCTs" in text
    assert "- EC1: Exclude reviews" in text
    assert "MET | NOT_MET | UNCLEAR" in text
    assert "TRIGGERED | NOT_TRIGGERED | UNCLEAR" in text
