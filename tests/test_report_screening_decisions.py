"""Report-tool screening decision parsing for criteria + UNCLEAR schema."""

from __future__ import annotations

import json
import unittest

from mentor.tools.report_tools import (
    _normalize_decision,
    _parse_decisions,
    extract_included_studies,
    format_report,
)


def _criteria_payload() -> dict:
    return {
        "n_total": 3,
        "n_included": 1,
        "n_excluded": 1,
        "n_unclear": 1,
        "decisions": [
            {
                "study_index": 1,
                "final_decision": "INCLUDE",
                "criteria": [
                    {
                        "id": "IC1",
                        "label": "MET",
                        "rationale": "Adults.",
                    },
                    {
                        "id": "EC1",
                        "label": "NOT_TRIGGERED",
                        "rationale": "Not a review.",
                    },
                ],
            },
            {
                "study_index": 2,
                "final_decision": "EXCLUDE",
                "criteria": [
                    {
                        "id": "IC1",
                        "label": "NOT_MET",
                        "rationale": "Pediatric only.",
                    },
                    {
                        "id": "EC1",
                        "label": "NOT_TRIGGERED",
                        "rationale": "Primary study.",
                    },
                ],
            },
            {
                "study_index": 3,
                "final_decision": "UNCLEAR",
                "criteria": [
                    {
                        "id": "IC1",
                        "label": "UNCLEAR",
                        "rationale": "Age not stated.",
                    },
                    {
                        "id": "EC1",
                        "label": "NOT_TRIGGERED",
                        "rationale": "Primary study.",
                    },
                ],
            },
        ],
    }


class NormalizeDecisionTests(unittest.TestCase):
    def test_prefers_final_decision_over_legacy_decision(self):
        normalized = _normalize_decision(
            {
                "study_index": 1,
                "final_decision": "UNCLEAR",
                "decision": "INCLUDE",
                "criteria": [{"id": "IC1", "label": "UNCLEAR", "rationale": "x"}],
            }
        )
        self.assertEqual(normalized["final_decision"], "UNCLEAR")
        self.assertEqual(len(normalized["criteria"]), 1)

    def test_falls_back_to_legacy_decision(self):
        normalized = _normalize_decision(
            {"study_index": 2, "decision": "EXCLUDE", "reason": "wrong age"}
        )
        self.assertEqual(normalized["final_decision"], "EXCLUDE")
        self.assertEqual(normalized["reason"], "wrong age")
        self.assertEqual(normalized["criteria"], [])


class ParseDecisionsTests(unittest.TestCase):
    def test_parses_criteria_schema_json(self):
        decisions = _parse_decisions(json.dumps(_criteria_payload()))
        self.assertEqual(len(decisions), 3)
        by_index = {d["study_index"]: d for d in decisions}
        self.assertEqual(by_index[1]["final_decision"], "INCLUDE")
        self.assertEqual(by_index[2]["final_decision"], "EXCLUDE")
        self.assertEqual(by_index[3]["final_decision"], "UNCLEAR")
        self.assertEqual(by_index[3]["criteria"][0]["id"], "IC1")

    def test_parses_final_decision_only_records(self):
        payload = {
            "decisions": [
                {"study_index": 1, "final_decision": "UNCLEAR", "criteria": []},
            ]
        }
        decisions = _parse_decisions(json.dumps(payload))
        self.assertEqual(decisions[0]["final_decision"], "UNCLEAR")
        self.assertNotIn("decision", decisions[0])

    def test_regex_fallback_accepts_final_decision_unclear(self):
        text = '{study_index: 7, final_decision: "UNCLEAR", reason: "vague"}'
        decisions = _parse_decisions(text)
        self.assertEqual(len(decisions), 1)
        self.assertEqual(decisions[0]["study_index"], 7)
        self.assertEqual(decisions[0]["final_decision"], "UNCLEAR")

    def test_simple_text_fallback_accepts_unclear(self):
        decisions = _parse_decisions("Study 4: UNCLEAR — age missing")
        self.assertEqual(len(decisions), 1)
        self.assertEqual(decisions[0]["final_decision"], "UNCLEAR")
        self.assertIn("age missing", decisions[0]["reason"])


class ExtractIncludedStudiesTests(unittest.TestCase):
    def test_mines_include_and_unclear_not_exclude(self):
        candidates = {
            "studies": [
                {"study_index": 1, "title": "A", "abstract": "a"},
                {"study_index": 2, "title": "B", "abstract": "b"},
                {"study_index": 3, "title": "C", "abstract": "c"},
            ]
        }
        included = json.loads(
            extract_included_studies(
                screening_response=json.dumps(_criteria_payload()),
                candidates_json=json.dumps(candidates),
            )
        )
        self.assertEqual([s["study_index"] for s in included], [1, 3])
        self.assertEqual(included[0]["title"], "A")
        self.assertEqual(included[1]["title"], "C")


class FormatReportTests(unittest.TestCase):
    def test_reports_unclear_count_and_criteria_detail(self):
        report = format_report(
            review_title="Demo",
            review_objective="Obj",
            num_candidates=3,
            screening_response=json.dumps(_criteria_payload()),
            evidence_response="{}",
            synthesis_response="{}",
        )
        self.assertIn("Included studies: 1", report)
        self.assertIn("Excluded studies: 1", report)
        self.assertIn("Unclear studies: 1", report)
        self.assertIn("Study 3: UNCLEAR", report)
        self.assertIn("IC1: UNCLEAR", report)
        self.assertIn("Age not stated.", report)


if __name__ == "__main__":
    unittest.main()
