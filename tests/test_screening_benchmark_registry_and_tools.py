"""Tests for review suite registry and screening persistence helpers."""

import json
import os
import tempfile
import unittest

from experiments.suites.review_suites import (
    expand_suite_run_config,
    get_review_suite,
    resolve_review_selection,
)
from mentor.tools.report_tools import _parse_decisions
from mentor.tools.screening_persistence import (
    append_chunk_decisions,
    read_existing_decisions,
    write_screening_artifacts,
)


class ScreeningBenchmarkRegistryAndToolsTests(unittest.TestCase):
    def test_screening_ladder_suite_contains_locked_reviews(self):
        suite = get_review_suite("screening_ladder")
        self.assertEqual(len(suite), 5)
        self.assertEqual(suite[0].key, "https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD000211.pub2/full")
        self.assertEqual(suite[-1].key, "https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD011845.pub2/full")

    def test_balanced_dev_ladder_suite_contains_expected_reviews(self):
        suite = get_review_suite("screening_ladder_dev_exclude_balanced")
        self.assertEqual(len(suite), 5)
        self.assertEqual(suite[0].key, "https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD001040.pub2/full")
        self.assertEqual(suite[-1].key, "https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD011589.pub2/full")
        self.assertEqual(suite[0].split, "dev")
        self.assertEqual(suite[-1].split, "dev")

    def test_no_label_0_5_dev_ladder_suite_contains_expected_reviews(self):
        suite = get_review_suite("screening_ladder_dev_no_label_0_5")
        self.assertEqual(len(suite), 5)
        self.assertEqual(suite[0].key, "https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD002900/full")
        self.assertEqual(suite[-1].key, "https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD014823/full")
        self.assertEqual(suite[0].split, "dev")
        self.assertEqual(suite[-1].split, "dev")

    def test_unknown_suite_name_is_rejected(self):
        with self.assertRaises(ValueError):
            get_review_suite("informative")

    def test_review_subset_resolution_preserves_order(self):
        subset = resolve_review_selection(
            "screening_ladder",
            ["https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD005654.pub4/full", "https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD000211.pub2/full"],
        )
        self.assertEqual(
            [review.key for review in subset],
            ["https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD005654.pub4/full", "https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD000211.pub2/full"],
        )

    def test_suite_without_run_requires_profiles_override(self):
        with self.assertRaises(ValueError):
            expand_suite_run_config("screening_ladder")

    def test_suite_profiles_override_expands_configurations(self):
        cfg = expand_suite_run_config(
            "screening_ladder",
            profiles_override=["openai_gpt5", "deepseek_v4_pro"],
            batch_size_override=10,
            repeats_override=2,
        )
        self.assertEqual(cfg.batch_size, 10)
        self.assertEqual(cfg.repeats, 2)
        self.assertEqual(
            [c.profile_key for c in cfg.configurations],
            ["openai_gpt5", "deepseek_v4_pro"],
        )
        self.assertEqual(cfg.configurations[0].agents["gatekeeper"], "openai_gpt5")

    def test_write_screening_artifacts_keeps_screening_only_shape(self):
        decisions = [
            {"study_index": 1, "decision": "INCLUDE", "rationale": "Matches criteria"},
            {"study_index": 2, "decision": "EXCLUDE", "rationale": "Wrong population"},
        ]
        with tempfile.TemporaryDirectory() as tmpdir:
            write_screening_artifacts(tmpdir, decisions, expected_n_studies=2)
            output_path = os.path.join(tmpdir, "evidence.json")
            self.assertTrue(os.path.exists(output_path))
            with open(output_path, "r", encoding="utf-8") as f:
                payload = json.load(f)

        self.assertEqual(set(payload), {"screening_decisions"})
        self.assertEqual(len(payload["screening_decisions"]), 2)

    def test_append_chunk_parses_python_literal_wrapper(self):
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
        # Ensure parser still understands the wrapper used by append.
        self.assertEqual(len(_parse_decisions(screening_response)), 2)

        with tempfile.TemporaryDirectory() as tmpdir:
            append_chunk_decisions(
                screening_response,
                tmpdir,
                [1, 2],
                expected_n_studies=2,
            )
            payload_decisions = read_existing_decisions(tmpdir)

        self.assertEqual(len(payload_decisions), 2)
        self.assertEqual(payload_decisions[0]["study_index"], 1)
        self.assertEqual(payload_decisions[1]["decision"], "EXCLUDE")

    def test_append_chunk_rejects_incomplete_decision_set(self):
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
                append_chunk_decisions(
                    screening_response,
                    tmpdir,
                    [1, 2],
                    expected_n_studies=2,
                )
