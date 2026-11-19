"""Tests for deterministic Gatekeeper final-decision rules."""

from __future__ import annotations

import json
import unittest

from mentor.tools.screening_tools import compute_final_decision, get_final_decision


def _ic(criterion_id: str, label: str) -> dict:
    return {"id": criterion_id, "label": label, "rationale": "x"}


def _ec(criterion_id: str, label: str) -> dict:
    return {"id": criterion_id, "label": label, "rationale": "x"}


class ComputeFinalDecisionTests(unittest.TestCase):
    def test_exclude_when_inclusion_not_met(self):
        self.assertEqual(
            compute_final_decision(
                [_ic("IC1", "NOT_MET"), _ec("EC1", "NOT_TRIGGERED")]
            ),
            "EXCLUDE",
        )

    def test_exclude_when_exclusion_triggered(self):
        self.assertEqual(
            compute_final_decision([_ic("IC1", "MET"), _ec("EC1", "TRIGGERED")]),
            "EXCLUDE",
        )

    def test_exclude_wins_over_unclear(self):
        self.assertEqual(
            compute_final_decision(
                [_ic("IC1", "NOT_MET"), _ic("IC2", "UNCLEAR"), _ec("EC1", "UNCLEAR")]
            ),
            "EXCLUDE",
        )

    def test_include_when_all_clear(self):
        self.assertEqual(
            compute_final_decision(
                [_ic("IC1", "MET"), _ic("IC2", "MET"), _ec("EC1", "NOT_TRIGGERED")]
            ),
            "INCLUDE",
        )

    def test_unclear_when_inclusion_unclear(self):
        self.assertEqual(
            compute_final_decision(
                [_ic("IC1", "MET"), _ic("IC2", "UNCLEAR"), _ec("EC1", "NOT_TRIGGERED")]
            ),
            "UNCLEAR",
        )

    def test_unclear_when_exclusion_unclear(self):
        self.assertEqual(
            compute_final_decision(
                [_ic("IC1", "MET"), _ec("EC1", "UNCLEAR")]
            ),
            "UNCLEAR",
        )

    def test_rejects_empty_criteria(self):
        with self.assertRaises(ValueError):
            compute_final_decision([])

    def test_rejects_unknown_id_without_type(self):
        with self.assertRaises(ValueError):
            compute_final_decision([{"id": "X1", "label": "MET"}])

    def test_accepts_explicit_type(self):
        self.assertEqual(
            compute_final_decision(
                [
                    {"id": "1", "type": "inclusion", "label": "MET"},
                    {"id": "2", "type": "exclusion", "label": "NOT_TRIGGERED"},
                ]
            ),
            "INCLUDE",
        )


class GetFinalDecisionToolTests(unittest.TestCase):
    def test_tool_accepts_json_array(self):
        payload = json.dumps([_ic("IC1", "MET"), _ec("EC1", "NOT_TRIGGERED")])
        self.assertEqual(get_final_decision(payload), "INCLUDE")

    def test_tool_accepts_wrapped_criteria_object(self):
        payload = json.dumps(
            {"criteria": [_ic("IC1", "UNCLEAR"), _ec("EC1", "NOT_TRIGGERED")]}
        )
        self.assertEqual(get_final_decision(payload), "UNCLEAR")


if __name__ == "__main__":
    unittest.main()
