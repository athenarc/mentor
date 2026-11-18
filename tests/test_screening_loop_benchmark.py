"""Tests for screening batch helpers and persistence."""

from __future__ import annotations

import json
import tempfile
import unittest

from mentor.tools.screening_loop import (
    append_screening_batch,
    get_screening_response_json,
    make_get_screening_batches_tool,
)
from mentor.tools.screening_persistence import (
    append_batch_decisions,
    batch_indices,
    read_existing_decisions,
)
from mentor.tools.search.search_tools import load_review_data


def _load_three_studies() -> None:
    load_review_data(
        json.dumps(
            {
                "title": "Demo review",
                "objective": "O",
                "background": "B",
                "selection_criteria": "S",
                "studies": [
                    {"study_index": 1, "title": "s1", "abstract": "a1"},
                    {"study_index": 2, "title": "s2", "abstract": "a2"},
                    {"study_index": 3, "title": "s3", "abstract": "a3"},
                ],
            }
        )
    )


def _decision_payload(indices: list[int], decision: str = "INCLUDE") -> str:
    return json.dumps(
        {
            "n_total": len(indices),
            "n_included": len(indices) if decision == "INCLUDE" else 0,
            "n_excluded": 0 if decision == "INCLUDE" else len(indices),
            "decisions": [
                {
                    "study_index": index,
                    "title": f"s{index}",
                    "decision": decision,
                    "rationale": f"reason {index}",
                    "confidence": "high",
                }
                for index in indices
            ],
        }
    )


class BatchIndicesTests(unittest.TestCase):
    def test_none_returns_one_batch(self):
        self.assertEqual(batch_indices([1, 2, 3], batch_size=None), [[1, 2, 3]])

    def test_size_one(self):
        self.assertEqual(batch_indices([1, 2, 3], batch_size=1), [[1], [2], [3]])

    def test_size_two(self):
        self.assertEqual(batch_indices([1, 2, 3], batch_size=2), [[1, 2], [3]])


class AppendBatchTests(unittest.TestCase):
    def test_append_batch_updates_evidence_and_progress(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            append_batch_decisions(
                _decision_payload([1, 2]),
                tmpdir,
                [1, 2],
                expected_n_studies=3,
            )
            decisions = read_existing_decisions(tmpdir)
            self.assertEqual([d["study_index"] for d in decisions], [1, 2])

            with self.assertRaises(ValueError):
                append_batch_decisions(
                    _decision_payload([1]),
                    tmpdir,
                    [1],
                    expected_n_studies=3,
                )

    def test_append_rejects_wrong_indices(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            with self.assertRaises(ValueError):
                append_batch_decisions(
                    _decision_payload([2]),
                    tmpdir,
                    [1],
                    expected_n_studies=1,
                )

    def test_append_screening_batch_tool(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            msg = append_screening_batch(
                _decision_payload([1]),
                tmpdir,
                json.dumps([1]),
                3,
            )
            self.assertIn("1/3", msg)
            self.assertEqual(len(read_existing_decisions(tmpdir)), 1)


class GetScreeningBatchesToolTests(unittest.TestCase):
    def test_batch_size_none_one_batch(self):
        _load_three_studies()
        with tempfile.TemporaryDirectory() as tmpdir:
            tool = make_get_screening_batches_tool(batch_size=None)
            batches = json.loads(tool.forward(tmpdir))
            self.assertEqual(len(batches), 1)
            self.assertEqual(batches[0]["indices"], [1, 2, 3])
            self.assertEqual(
                [s["study_index"] for s in batches[0]["payload"]["studies"]],
                [1, 2, 3],
            )
            self.assertEqual(batches[0]["payload"]["n_total"], 3)

    def test_batch_size_one(self):
        _load_three_studies()
        with tempfile.TemporaryDirectory() as tmpdir:
            tool = make_get_screening_batches_tool(batch_size=1)
            batches = json.loads(tool.forward(tmpdir))
            self.assertEqual(len(batches), 3)
            self.assertEqual([b["indices"] for b in batches], [[1], [2], [3]])

    def test_batch_size_two(self):
        _load_three_studies()
        with tempfile.TemporaryDirectory() as tmpdir:
            tool = make_get_screening_batches_tool(batch_size=2)
            batches = json.loads(tool.forward(tmpdir))
            self.assertEqual(len(batches), 2)
            self.assertEqual(batches[0]["indices"], [1, 2])
            self.assertEqual(batches[1]["indices"], [3])

    def test_resume_skips_saved_decisions(self):
        _load_three_studies()
        with tempfile.TemporaryDirectory() as tmpdir:
            append_batch_decisions(
                _decision_payload([1]),
                tmpdir,
                [1],
                expected_n_studies=3,
            )
            tool = make_get_screening_batches_tool(batch_size=None)
            batches = json.loads(tool.forward(tmpdir))
            self.assertEqual(len(batches), 1)
            self.assertEqual(batches[0]["indices"], [2, 3])
            self.assertEqual(
                [s["study_index"] for s in batches[0]["payload"]["studies"]],
                [2, 3],
            )

    def test_all_done_returns_empty(self):
        _load_three_studies()
        with tempfile.TemporaryDirectory() as tmpdir:
            append_batch_decisions(
                _decision_payload([1, 2, 3]),
                tmpdir,
                [1, 2, 3],
                expected_n_studies=3,
            )
            tool = make_get_screening_batches_tool(batch_size=None)
            self.assertEqual(tool.forward(tmpdir), "[]")

    def test_get_screening_response_json(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            append_batch_decisions(
                _decision_payload([1, 2]),
                tmpdir,
                [1, 2],
                expected_n_studies=2,
            )
            payload = json.loads(get_screening_response_json(tmpdir))
            self.assertEqual(payload["n_total"], 2)
            self.assertEqual(payload["n_included"], 2)


if __name__ == "__main__":
    unittest.main()
