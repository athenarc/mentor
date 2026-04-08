import unittest

from bastirr.benchmarking.metrics import (
    compute_screening_metrics,
    describe_screening_label_policy,
    gold_label_to_screening_decision,
)
from bastirr.data import Study, SystematicReview


class ScreeningBenchmarkMetricsTests(unittest.TestCase):
    def test_half_label_counts_as_screen_pass(self):
        self.assertEqual(gold_label_to_screening_decision(1.0), "INCLUDE")
        self.assertEqual(gold_label_to_screening_decision(0.5), "INCLUDE")
        self.assertEqual(gold_label_to_screening_decision(0.0), "EXCLUDE")

    def test_half_label_can_count_as_exclude_under_final_review_policy(self):
        self.assertEqual(
            gold_label_to_screening_decision(0.5, label_policy="exclude_label_0_5"),
            "EXCLUDE",
        )
        self.assertIn(
            "1.0 counts as INCLUDE",
            describe_screening_label_policy("exclude_label_0_5"),
        )

    def test_compute_metrics_handles_partial_decisions(self):
        review = SystematicReview(
            review_url="https://example.test/review",
            title="Synthetic Review",
            background="Background",
            objective="Objective",
            selection_criteria="Criteria",
            studies=[
                Study(title="A", abstract="A", label=1.0),
                Study(title="B", abstract="B", label=0.5),
                Study(title="C", abstract="C", label=0.0),
                Study(title="D", abstract="D", label=0.0),
            ],
        )
        decisions = [
            {"study_index": 1, "decision": "INCLUDE"},
            {"study_index": 2, "decision": "EXCLUDE"},
            {"study_index": 3, "decision": "INCLUDE"},
        ]

        metrics = compute_screening_metrics(review, decisions)

        self.assertEqual(metrics["gold_pass_count"], 2)
        self.assertEqual(metrics["gold_exclude_count"], 2)
        self.assertEqual(metrics["screening_decision_count"], 3)
        self.assertEqual(metrics["missing_decision_count"], 1)
        self.assertAlmostEqual(metrics["decision_coverage"], 0.75)
        self.assertFalse(metrics["parse_success"])

        self.assertEqual(metrics["tp"], 1)
        self.assertEqual(metrics["fn"], 1)
        self.assertEqual(metrics["fp"], 1)
        self.assertEqual(metrics["tn"], 1)

        self.assertAlmostEqual(metrics["accuracy"], 0.5)
        self.assertAlmostEqual(metrics["precision"], 0.5)
        self.assertAlmostEqual(metrics["recall"], 0.5)
        self.assertAlmostEqual(metrics["specificity"], 0.5)
        self.assertAlmostEqual(metrics["f1"], 0.5)

    def test_compute_metrics_supports_final_review_policy(self):
        review = SystematicReview(
            review_url="https://example.test/review",
            title="Synthetic Review",
            background="Background",
            objective="Objective",
            selection_criteria="Criteria",
            studies=[
                Study(title="A", abstract="A", label=1.0),
                Study(title="B", abstract="B", label=0.5),
                Study(title="C", abstract="C", label=0.0),
            ],
        )
        decisions = [
            {"study_index": 1, "decision": "INCLUDE"},
            {"study_index": 2, "decision": "EXCLUDE"},
            {"study_index": 3, "decision": "EXCLUDE"},
        ]

        metrics = compute_screening_metrics(
            review,
            decisions,
            label_policy="exclude_label_0_5",
        )

        self.assertEqual(metrics["gold_label_policy"], "exclude_label_0_5")
        self.assertEqual(metrics["gold_pass_count"], 1)
        self.assertEqual(metrics["gold_exclude_count"], 2)
        self.assertEqual(metrics["tp"], 1)
        self.assertEqual(metrics["fp"], 0)
        self.assertEqual(metrics["tn"], 2)
        self.assertEqual(metrics["fn"], 0)
        self.assertAlmostEqual(metrics["precision"], 1.0)
        self.assertAlmostEqual(metrics["recall"], 1.0)
