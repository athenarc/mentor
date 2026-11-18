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


def _decision(
    index: int = 1,
    *,
    title: str | None = None,
    decision: str = "INCLUDE",
) -> dict:
    return {
        "study_index": index,
        "title": title or f"s{index}",
        "decision": decision,
        "reason": f"reason {index}",
        "confidence": "high",
    }


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
