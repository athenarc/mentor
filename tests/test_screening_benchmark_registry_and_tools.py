import json
import os
import tempfile
import unittest

from bastirr.benchmarking.review_suites import get_review_suite, resolve_review_selection
from bastirr.tools.screening_benchmark_tools import save_screening_evidence_json


class ScreeningBenchmarkRegistryAndToolsTests(unittest.TestCase):
    def test_screening_ladder_suite_contains_locked_reviews(self):
        suite = get_review_suite("screening_ladder")
        self.assertEqual(len(suite), 5)
        self.assertEqual(suite[0].key, "stroke_theophylline_10")
        self.assertEqual(suite[-1].key, "heart_failure_mhealth_200")
        self.assertEqual(suite[0].expected_n_studies, 10)
        self.assertEqual(suite[-1].expected_n_studies, 200)

    def test_unknown_suite_name_is_rejected(self):
        with self.assertRaises(ValueError):
            get_review_suite("informative")

    def test_review_subset_resolution_preserves_order(self):
        subset = resolve_review_selection(
            "screening_ladder",
            ["pelvic_floor_training_100", "stroke_theophylline_10"],
        )
        self.assertEqual(
            [review.key for review in subset],
            ["pelvic_floor_training_100", "stroke_theophylline_10"],
        )

    def test_save_screening_evidence_json_keeps_screening_only_shape(self):
        screening_response = json.dumps({
            "n_total": 2,
            "n_included": 1,
            "n_excluded": 1,
            "decisions": [
                {
                    "study_index": 1,
                    "decision": "INCLUDE",
                    "rationale": "Matches criteria",
                },
                {
                    "study_index": 2,
                    "decision": "EXCLUDE",
                    "rationale": "Wrong population",
                },
            ],
        })

        with tempfile.TemporaryDirectory() as tmpdir:
            save_screening_evidence_json(
                screening_response=screening_response,
                output_dir=tmpdir,
            )
            output_path = os.path.join(tmpdir, "evidence.json")
            self.assertTrue(os.path.exists(output_path))

            with open(output_path, "r", encoding="utf-8") as f:
                payload = json.load(f)

        self.assertEqual(set(payload), {"screening_decisions"})
        self.assertEqual(len(payload["screening_decisions"]), 2)
