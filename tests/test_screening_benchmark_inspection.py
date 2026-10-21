"""Tests for screening inspection JSON/markdown artifact generation."""

import json
import tempfile
import unittest
from pathlib import Path

from experiments.harness.inspection import (
    build_screening_inspection_payload,
    write_screening_inspection_artifacts,
)
from experiments.harness.metrics import compute_screening_metrics
from experiments.dataset import Study, SystematicReview


class ScreeningBenchmarkInspectionTests(unittest.TestCase):
    def test_inspection_payload_captures_gold_and_prediction_context(self):
        review = SystematicReview(
            review_url="https://example.test/review",
            title="Synthetic Review",
            background="Background",
            objective="Objective",
            selection_criteria="Criteria",
            studies=[
                Study(title="Study A", abstract="Abstract A", label=1.0),
                Study(title="Study B", abstract="Abstract B", label=0.5),
                Study(title="Study C", abstract="Abstract C", label=0.0),
            ],
        )
        decisions = [
            {"study_index": 1, "decision": "INCLUDE", "reason": "Matches criteria."},
            {"study_index": 2, "decision": "EXCLUDE", "reason": "Wrong design."},
        ]
        metrics = compute_screening_metrics(review, decisions)

        payload = build_screening_inspection_payload(review, decisions, metrics)

        self.assertEqual(payload["screening_criteria"], "Criteria")
        self.assertEqual(payload["gold_label_policy"], "include_label_0_5")
        self.assertEqual(payload["summary"]["match_count"], 1)
        self.assertEqual(payload["summary"]["mismatch_count"], 1)
        self.assertEqual(payload["summary"]["missing_decision_count"], 1)

        first = payload["studies"][0]
        second = payload["studies"][1]
        third = payload["studies"][2]

        self.assertEqual(first["gold_screening_decision"], "INCLUDE")
        self.assertEqual(first["gold_review_outcome"], "included_in_review")
        self.assertEqual(first["match_status"], "correct")

        self.assertEqual(second["gold_screening_decision"], "INCLUDE")
        self.assertEqual(second["gold_review_outcome"], "excluded_after_full_text")
        self.assertEqual(second["predicted_decision"], "EXCLUDE")
        self.assertEqual(second["match_status"], "incorrect")

        self.assertEqual(third["gold_screening_decision"], "EXCLUDE")
        self.assertEqual(third["predicted_decision"], "")
        self.assertEqual(third["match_status"], "missing")

    def test_inspection_payload_reflects_alternate_gold_label_policy(self):
        review = SystematicReview(
            review_url="https://example.test/review",
            title="Synthetic Review",
            background="Background",
            objective="Objective",
            selection_criteria="Criteria",
            studies=[
                Study(title="Study A", abstract="Abstract A", label=1.0),
                Study(title="Study B", abstract="Abstract B", label=0.5),
            ],
        )
        decisions = [
            {"study_index": 1, "decision": "INCLUDE", "reason": "Matches criteria."},
            {"study_index": 2, "decision": "EXCLUDE", "reason": "Insufficient signal."},
        ]
        metrics = compute_screening_metrics(
            review,
            decisions,
            label_policy="exclude_label_0_5",
        )

        payload = build_screening_inspection_payload(review, decisions, metrics)

        self.assertEqual(payload["gold_label_policy"], "exclude_label_0_5")
        self.assertEqual(payload["gold_screening_policy"]["0.5"], "EXCLUDE")
        self.assertEqual(payload["studies"][1]["gold_screening_decision"], "EXCLUDE")

    def test_write_inspection_artifacts_creates_json_and_markdown(self):
        review = SystematicReview(
            review_url="https://example.test/review",
            title="Synthetic Review",
            background="Background",
            objective="Objective",
            selection_criteria="Criteria",
            studies=[
                Study(title="Study A", abstract="Abstract A", label=1.0),
                Study(title="Study B", abstract="Abstract B", label=0.0),
            ],
        )
        decisions = [
            {"study_index": 1, "decision": "INCLUDE", "reason": "Matches criteria."},
            {"study_index": 2, "decision": "INCLUDE", "reason": "Incorrect include."},
        ]
        metrics = compute_screening_metrics(review, decisions)

        with tempfile.TemporaryDirectory() as tmpdir:
            paths = write_screening_inspection_artifacts(
                run_dir=Path(tmpdir),
                review=review,
                screening_decisions=decisions,
                metrics=metrics,
            )

            json_path = Path(paths["screening_inspection_json"])
            markdown_path = Path(paths["screening_inspection_markdown"])

            self.assertTrue(json_path.exists())
            self.assertTrue(markdown_path.exists())

            payload = json.loads(json_path.read_text(encoding="utf-8"))
            markdown = markdown_path.read_text(encoding="utf-8")

        self.assertEqual(payload["summary"]["mismatch_count"], 1)
        self.assertEqual(payload["screening_criteria"], "Criteria")
        self.assertIn("**Screening criteria:** Criteria", markdown)
        self.assertIn("**Gold label policy:** `include_label_0_5`", markdown)
        self.assertIn("## Mismatches", markdown)
        self.assertIn("Study B", markdown)
        self.assertIn("incorrect", markdown)
