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

    def test_balanced_dev_ladder_suite_contains_expected_reviews(self):
        suite = get_review_suite("screening_ladder_dev_exclude_balanced")
        self.assertEqual(len(suite), 5)
        self.assertEqual(suite[0].key, "endometrial_progestagens_10")
        self.assertEqual(suite[-1].key, "prom_feedback_194")
        self.assertEqual(suite[0].split, "dev")
        self.assertEqual(suite[-1].split, "dev")
        self.assertEqual(suite[2].expected_n_studies, 50)
        self.assertEqual(suite[-1].expected_n_studies, 194)

    def test_no_label_0_5_dev_ladder_suite_contains_expected_reviews(self):
        suite = get_review_suite("screening_ladder_dev_no_label_0_5")
        self.assertEqual(len(suite), 5)
        self.assertEqual(suite[0].key, "surgical_termination_10")
        self.assertEqual(suite[-1].key, "home_based_rehabilitation_183")
        self.assertEqual(suite[0].split, "dev")
        self.assertEqual(suite[-1].split, "dev")
        self.assertEqual(suite[1].expected_n_studies, 24)
        self.assertEqual(suite[3].expected_n_studies, 92)

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

    def test_save_screening_evidence_json_parses_python_literal_wrapper(self):
        screening_response = """{
            'screening_json': {
                'decisions': [
                    {
                        'study_index': 1,
                        'decision': 'INCLUDE',
                        'rationale': 'Eligible population'
                    },
                    {
                        'study_index': 2,
                        'decision': 'EXCLUDE',
                        'rationale': 'Wrong intervention'
                    }
                ]
            }
        }"""

        with tempfile.TemporaryDirectory() as tmpdir:
            save_screening_evidence_json(
                screening_response=screening_response,
                output_dir=tmpdir,
            )
            output_path = os.path.join(tmpdir, "evidence.json")
            with open(output_path, "r", encoding="utf-8") as f:
                payload = json.load(f)

        self.assertEqual(len(payload["screening_decisions"]), 2)
        self.assertEqual(payload["screening_decisions"][0]["study_index"], 1)
        self.assertEqual(payload["screening_decisions"][1]["decision"], "EXCLUDE")

    def test_save_screening_evidence_json_rejects_incomplete_decision_set(self):
        screening_response = json.dumps({
            "n_total": 2,
            "n_included": 1,
            "n_excluded": 1,
            "decisions": [
                {
                    "study_index": 1,
                    "decision": "INCLUDE",
                    "rationale": "Matches criteria",
                }
            ],
        })

        with tempfile.TemporaryDirectory() as tmpdir:
            with self.assertRaises(ValueError):
                save_screening_evidence_json(
                    screening_response=screening_response,
                    output_dir=tmpdir,
                    expected_n_studies=2,
                )
