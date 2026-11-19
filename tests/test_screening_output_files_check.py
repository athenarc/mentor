"""Tests for screening artifact consistency validation."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from mentor.tools.screening_persistence import (
    append_batch_decisions,
    write_screening_artifacts,
)
from mentor.tools.validation import validate_screening_artifacts_consistent


def _criteria_for(decision: str) -> list[dict]:
    if decision == "INCLUDE":
        return [
            {"id": "IC1", "label": "MET", "rationale": "ok"},
            {"id": "EC1", "label": "NOT_TRIGGERED", "rationale": "ok"},
        ]
    if decision == "EXCLUDE":
        return [
            {"id": "IC1", "label": "NOT_MET", "rationale": "ok"},
            {"id": "EC1", "label": "NOT_TRIGGERED", "rationale": "ok"},
        ]
    return [
        {"id": "IC1", "label": "UNCLEAR", "rationale": "ok"},
        {"id": "EC1", "label": "NOT_TRIGGERED", "rationale": "ok"},
    ]


def _decision(index: int = 1, *, decision: str = "INCLUDE") -> dict:
    return {
        "study_index": index,
        "criteria": _criteria_for(decision),
        "final_decision": decision,
    }


def _decision_payload(indices: list[int], decision: str = "INCLUDE") -> str:
    counts = {"INCLUDE": 0, "EXCLUDE": 0, "UNCLEAR": 0}
    counts[decision] = len(indices)
    return json.dumps(
        {
            "n_total": len(indices),
            "n_included": counts["INCLUDE"],
            "n_excluded": counts["EXCLUDE"],
            "n_unclear": counts["UNCLEAR"],
            "decisions": [
                {
                    "study_index": index,
                    "criteria": _criteria_for(decision),
                    "final_decision": decision,
                }
                for index in indices
            ],
        }
    )


class ScreeningArtifactsConsistentTests(unittest.TestCase):
    def test_consistent_artifacts_pass(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            append_batch_decisions(
                _decision_payload([1, 2]),
                tmpdir,
                [1, 2],
                expected_n_studies=2,
            )
            validate_screening_artifacts_consistent(tmpdir, expected_n_studies=2)

    def test_append_accepts_unclear(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            updated = append_batch_decisions(
                _decision_payload([1], decision="UNCLEAR"),
                tmpdir,
                [1],
                expected_n_studies=1,
            )
            self.assertEqual(updated[0]["final_decision"], "UNCLEAR")

    def test_detects_progress_mismatch(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            write_screening_artifacts(
                tmpdir,
                [_decision()],
                expected_n_studies=1,
            )
            progress = Path(tmpdir) / "screening_progress.json"
            payload = json.loads(progress.read_text(encoding="utf-8"))
            payload["completed_count"] = 99
            progress.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaises(ValueError) as ctx:
                validate_screening_artifacts_consistent(tmpdir, expected_n_studies=1)
            self.assertIn("completed_count", str(ctx.exception))

    def test_detects_missing_files(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            with self.assertRaises(ValueError) as ctx:
                validate_screening_artifacts_consistent(tmpdir, expected_n_studies=1)
            message = str(ctx.exception)
            self.assertIn("evidence.json", message)
            self.assertIn("screening_progress.json", message)

    def test_detects_decision_mismatch_between_files(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            write_screening_artifacts(
                tmpdir,
                [_decision()],
                expected_n_studies=1,
            )
            progress = Path(tmpdir) / "screening_progress.json"
            payload = json.loads(progress.read_text(encoding="utf-8"))
            payload["screening_decisions"][0]["final_decision"] = "EXCLUDE"
            payload["screening_decisions"][0]["decision"] = "EXCLUDE"
            progress.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaises(ValueError) as ctx:
                validate_screening_artifacts_consistent(tmpdir, expected_n_studies=1)
            self.assertIn("do not match", str(ctx.exception))

    def test_detects_bad_next_study_index(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            write_screening_artifacts(
                tmpdir,
                [_decision()],
                expected_n_studies=1,
            )
            progress = Path(tmpdir) / "screening_progress.json"
            payload = json.loads(progress.read_text(encoding="utf-8"))
            payload["next_study_index"] = 1
            progress.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaises(ValueError) as ctx:
                validate_screening_artifacts_consistent(tmpdir, expected_n_studies=1)
            self.assertIn("next_study_index", str(ctx.exception))

    def test_detects_bad_completed_indices(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            write_screening_artifacts(
                tmpdir,
                [_decision()],
                expected_n_studies=1,
            )
            progress = Path(tmpdir) / "screening_progress.json"
            payload = json.loads(progress.read_text(encoding="utf-8"))
            payload["completed_study_indices"] = [2]
            progress.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaises(ValueError) as ctx:
                validate_screening_artifacts_consistent(tmpdir, expected_n_studies=1)
            self.assertIn("completed indices", str(ctx.exception))

    def test_write_runs_consistency_check_when_complete(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch(
                "mentor.tools.validation.validate_screening_artifacts_consistent"
            ) as mock_validate:
                write_screening_artifacts(
                    tmpdir,
                    [_decision()],
                    expected_n_studies=1,
                )
            mock_validate.assert_called_once_with(tmpdir, expected_n_studies=1)

    def test_write_skips_consistency_check_when_incomplete(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch(
                "mentor.tools.validation.validate_screening_artifacts_consistent"
            ) as mock_validate:
                write_screening_artifacts(
                    tmpdir,
                    [_decision()],
                    expected_n_studies=2,
                )
            mock_validate.assert_not_called()


if __name__ == "__main__":
    unittest.main()
