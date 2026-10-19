"""Tests for systematic review and protocol JSON serialization helpers."""

import json
from types import SimpleNamespace

from mentor.runtime.session import protocol_to_json, review_to_json


def test_review_to_json_includes_n_total_and_studies():
    review = SimpleNamespace(
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
    assert payload["n_total"] == 2
    assert payload["studies"][0]["study_index"] == 1
    assert "label" not in payload["studies"][0]


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
