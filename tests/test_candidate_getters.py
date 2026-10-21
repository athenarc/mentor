"""Chunk payload helper: single index equals chunk of size one."""

from __future__ import annotations

import json

from mentor.tools.search.search_tools import (
    _candidate_studies_chunk_payload,
    load_review_data,
)


def test_single_index_matches_chunk_size_one():
    payload = {
        "title": "T",
        "objective": "O",
        "background": "B",
        "selection_criteria": "S",
        "studies": [
            {"study_index": 1, "title": "s1", "abstract": "a1"},
            {"study_index": 2, "title": "s2", "abstract": "a2"},
        ],
    }
    load_review_data(json.dumps(payload))
    single = _candidate_studies_chunk_payload("[2]")
    chunk = _candidate_studies_chunk_payload("[2]")
    assert json.loads(single) == json.loads(chunk)
    assert len(json.loads(single)["studies"]) == 1
    assert json.loads(single)["studies"][0]["study_index"] == 2
