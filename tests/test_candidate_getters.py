"""Exact equivalence: single-study getter == chunk getter with one index."""

from __future__ import annotations

import json

from mentor.tools.search.search_tools import (
    get_candidate_studies_chunk_json,
    get_candidate_study_json,
    load_review_data,
)


def test_get_candidate_study_json_matches_chunk_size_one():
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
    # smolagents Tool objects expose .forward / callable depending on version
    single = get_candidate_study_json(2)
    if not isinstance(single, str):
        single = get_candidate_study_json.forward(2)
    chunk = get_candidate_studies_chunk_json("[2]")
    if not isinstance(chunk, str):
        chunk = get_candidate_studies_chunk_json.forward("[2]")
    assert json.loads(single) == json.loads(chunk)
