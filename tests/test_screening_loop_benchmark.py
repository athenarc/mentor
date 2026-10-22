"""Tests for Python batch screening loop (screen_candidates) and persistence."""

from __future__ import annotations

import json
import tempfile
import unittest
from unittest.mock import MagicMock

from mentor.tools.screening_loop import make_screen_candidates_tool
from mentor.tools.screening_persistence import (
    append_chunk_decisions,
    chunk_indices,
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


class ChunkIndicesTests(unittest.TestCase):
    def test_none_returns_one_batch(self):
        self.assertEqual(chunk_indices([1, 2, 3], chunk_size=None), [[1, 2, 3]])

    def test_size_one(self):
        self.assertEqual(chunk_indices([1, 2, 3], chunk_size=1), [[1], [2], [3]])

    def test_size_two(self):
        self.assertEqual(chunk_indices([1, 2, 3], chunk_size=2), [[1, 2], [3]])


class AppendChunkTests(unittest.TestCase):
    def test_append_chunk_updates_evidence_and_progress(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            append_chunk_decisions(
                _decision_payload([1, 2]),
                tmpdir,
                [1, 2],
                expected_n_studies=3,
            )
            decisions = read_existing_decisions(tmpdir)
            self.assertEqual([d["study_index"] for d in decisions], [1, 2])

            with self.assertRaises(ValueError):
                append_chunk_decisions(
                    _decision_payload([1]),
                    tmpdir,
                    [1],
                    expected_n_studies=3,
                )

    def test_append_rejects_wrong_indices(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            with self.assertRaises(ValueError):
                append_chunk_decisions(
                    _decision_payload([2]),
                    tmpdir,
                    [1],
                    expected_n_studies=1,
                )


class ScreenCandidatesToolTests(unittest.TestCase):
    def test_batch_size_none_one_gatekeeper_call(self):
        _load_three_studies()
        gatekeeper = MagicMock(return_value=_decision_payload([1, 2, 3]))
        with tempfile.TemporaryDirectory() as tmpdir:
            tool = make_screen_candidates_tool(
                gatekeeper, batch_size=None, output_dir=tmpdir
            )
            result = tool.forward()
            self.assertEqual(gatekeeper.call_count, 1)
            payload = json.loads(result)
            self.assertEqual(payload["n_total"], 3)
            self.assertEqual(len(read_existing_decisions(tmpdir)), 3)

    def test_batch_size_one(self):
        _load_three_studies()

        def _side_effect(task, additional_args=None, **kwargs):
            studies = json.loads(additional_args["screening_payload"])["studies"]
            return _decision_payload([studies[0]["study_index"]])

        gatekeeper = MagicMock(side_effect=_side_effect)
        with tempfile.TemporaryDirectory() as tmpdir:
            tool = make_screen_candidates_tool(
                gatekeeper, batch_size=1, output_dir=tmpdir
            )
            tool.forward()
            self.assertEqual(gatekeeper.call_count, 3)
            self.assertEqual(
                [d["study_index"] for d in read_existing_decisions(tmpdir)],
                [1, 2, 3],
            )

    def test_batch_size_two(self):
        _load_three_studies()

        def _side_effect(task, additional_args=None, **kwargs):
            studies = json.loads(additional_args["screening_payload"])["studies"]
            return _decision_payload([s["study_index"] for s in studies])

        gatekeeper = MagicMock(side_effect=_side_effect)
        with tempfile.TemporaryDirectory() as tmpdir:
            tool = make_screen_candidates_tool(
                gatekeeper, batch_size=2, output_dir=tmpdir
            )
            tool.forward()
            self.assertEqual(gatekeeper.call_count, 2)

    def test_resume_skips_saved_decisions(self):
        _load_three_studies()
        with tempfile.TemporaryDirectory() as tmpdir:
            append_chunk_decisions(
                _decision_payload([1]),
                tmpdir,
                [1],
                expected_n_studies=3,
            )

            def _side_effect(task, additional_args=None, **kwargs):
                studies = json.loads(additional_args["screening_payload"])["studies"]
                return _decision_payload([s["study_index"] for s in studies])

            gatekeeper = MagicMock(side_effect=_side_effect)
            tool = make_screen_candidates_tool(
                gatekeeper, batch_size=None, output_dir=tmpdir
            )
            tool.forward()
            self.assertEqual(gatekeeper.call_count, 1)
            args = gatekeeper.call_args.kwargs.get("additional_args") or gatekeeper.call_args[1].get(
                "additional_args"
            )
            if args is None:
                # positional additional_args
                args = gatekeeper.call_args[0][1] if len(gatekeeper.call_args[0]) > 1 else gatekeeper.call_args[1]
            # MagicMock: call was gatekeeper("", additional_args={...})
            call_kwargs = gatekeeper.call_args.kwargs
            if not call_kwargs:
                # smolagents-style positional
                call_args = gatekeeper.call_args
                additional = call_args.kwargs.get("additional_args")
                if additional is None and len(call_args.args) >= 2:
                    additional = call_args.args[1]
            else:
                additional = call_kwargs["additional_args"]
            studies = json.loads(additional["screening_payload"])["studies"]
            self.assertEqual([s["study_index"] for s in studies], [2, 3])

    def test_retry_then_fail_closed(self):
        _load_three_studies()
        gatekeeper = MagicMock(side_effect=RuntimeError("boom"))
        with tempfile.TemporaryDirectory() as tmpdir:
            tool = make_screen_candidates_tool(
                gatekeeper,
                batch_size=None,
                output_dir=tmpdir,
                max_batch_attempts=2,
            )
            with self.assertRaises(ValueError) as ctx:
                tool.forward()
            self.assertIn("after 2 attempt", str(ctx.exception))
            self.assertEqual(gatekeeper.call_count, 2)
            self.assertEqual(read_existing_decisions(tmpdir), [])


if __name__ == "__main__":
    unittest.main()
