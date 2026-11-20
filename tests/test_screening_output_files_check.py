"""Tests for screening evidence.json validation."""

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
        "decision": decision,
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
            "study_decisions": [
                {
                    "study_index": index,
                    "criteria": _criteria_for(decision),
                    "decision": decision,
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
            self.assertFalse(
                (Path(tmpdir) / "screening_progress.json").exists()
            )

    def test_append_accepts_unclear(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            updated = append_batch_decisions(
                _decision_payload([1], decision="UNCLEAR"),
                tmpdir,
                [1],
                expected_n_studies=1,
            )
            self.assertEqual(updated[0]["decision"], "UNCLEAR")

    def test_evidence_json_matches_gatekeeper_shape(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            append_batch_decisions(
                _decision_payload([1], decision="INCLUDE"),
                tmpdir,
                [1],
                expected_n_studies=1,
            )
            payload = json.loads(
                (Path(tmpdir) / "evidence.json").read_text(encoding="utf-8")
            )
            self.assertEqual(payload["n_total"], 1)
            self.assertEqual(payload["n_included"], 1)
            self.assertEqual(payload["n_excluded"], 0)
            self.assertEqual(payload["n_unclear"], 0)
            self.assertIn("study_decisions", payload)
            self.assertNotIn("decisions", payload)
            self.assertNotIn("screening_decisions", payload)
            self.assertNotIn("final_decision", payload["study_decisions"][0])
            self.assertEqual(payload["study_decisions"][0]["decision"], "INCLUDE")

    def test_detects_missing_evidence_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            with self.assertRaises(ValueError) as ctx:
                validate_screening_artifacts_consistent(tmpdir, expected_n_studies=1)
            self.assertIn("evidence.json", str(ctx.exception))

    def test_detects_count_mismatch(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            write_screening_artifacts(
                tmpdir,
                [_decision()],
                expected_n_studies=1,
            )
            evidence = Path(tmpdir) / "evidence.json"
            payload = json.loads(evidence.read_text(encoding="utf-8"))
            payload["n_included"] = 0
            evidence.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaises(ValueError) as ctx:
                validate_screening_artifacts_consistent(tmpdir, expected_n_studies=1)
            self.assertIn("n_included", str(ctx.exception))

    def test_detects_incomplete_study_coverage(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            write_screening_artifacts(
                tmpdir,
                [_decision()],
                expected_n_studies=2,
            )
            with self.assertRaises(ValueError) as ctx:
                validate_screening_artifacts_consistent(tmpdir, expected_n_studies=2)
            self.assertIn("missing", str(ctx.exception))

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
