"""Tests for strict Gatekeeper final-answer validation."""

from __future__ import annotations

import json
import unittest

from mentor.tools.validation import validate_gatekeeper_answer


def _study(index: int = 1, title: str = "Example title") -> dict:
    return {
        "study_index": index,
        "title": title,
        "abstract": "Abstract text.",
    }


def _criteria_for(decision: str) -> list[dict]:
    if decision == "INCLUDE":
        return [
            {"id": "IC1", "label": "MET", "rationale": "Population matches."},
            {
                "id": "EC1",
                "label": "NOT_TRIGGERED",
                "rationale": "No exclusion applies.",
            },
        ]
    if decision == "EXCLUDE":
        return [
            {
                "id": "IC1",
                "label": "NOT_MET",
                "rationale": "Wrong population.",
            },
            {
                "id": "EC1",
                "label": "NOT_TRIGGERED",
                "rationale": "No exclusion applies.",
            },
        ]
    return [
        {"id": "IC1", "label": "UNCLEAR", "rationale": "Abstract is vague."},
        {
            "id": "EC1",
            "label": "NOT_TRIGGERED",
            "rationale": "No exclusion applies.",
        },
    ]


def _answer(studies: list[dict], *, decision: str = "INCLUDE") -> str:
    counts = {"INCLUDE": 0, "EXCLUDE": 0, "UNCLEAR": 0}
    counts[decision] = len(studies)
    return json.dumps(
        {
            "n_total": len(studies),
            "n_included": counts["INCLUDE"],
            "n_excluded": counts["EXCLUDE"],
            "n_unclear": counts["UNCLEAR"],
            "decisions": [
                {
                    "study_index": study["study_index"],
                    "criteria": _criteria_for(decision),
                    "final_decision": decision,
                }
                for study in studies
            ],
        }
    )


def _mutate_answer(studies: list[dict], mutator) -> str:
    payload = json.loads(_answer(studies))
    mutator(payload)
    return json.dumps(payload)


class ValidateGatekeeperAnswerTests(unittest.TestCase):
    def test_accepts_valid_answer(self):
        studies = [_study()]
        self.assertTrue(validate_gatekeeper_answer(_answer(studies), studies))

    def test_accepts_unclear(self):
        studies = [_study()]
        self.assertTrue(
            validate_gatekeeper_answer(_answer(studies, decision="UNCLEAR"), studies)
        )

    def test_rejects_non_string_answer(self):
        with self.assertRaises(ValueError) as ctx:
            validate_gatekeeper_answer({"n_total": 1}, [_study()])
        self.assertIn("JSON string", str(ctx.exception))

    def test_rejects_missing_decision(self):
        studies = [_study(1), _study(2, title="Other")]
        partial = json.loads(_answer([studies[0]]))
        partial["n_total"] = 1
        with self.assertRaises(ValueError):
            validate_gatekeeper_answer(json.dumps(partial), studies)

    def test_rejects_duplicate_json_keys(self):
        studies = [_study()]
        raw = (
            '{"n_total": 1, "n_included": 1, "n_excluded": 0, "n_unclear": 0, '
            '"decisions": [{"study_index": 1, "criteria": '
            '[{"id": "IC1", "label": "MET", "rationale": "ok"}, '
            '{"id": "EC1", "label": "NOT_TRIGGERED", "rationale": "ok"}], '
            '"final_decision": "INCLUDE"}], '
            '"n_total": 2}'
        )
        with self.assertRaises(ValueError):
            validate_gatekeeper_answer(raw, studies)

    def test_rejects_nan_constant(self):
        studies = [_study()]
        raw = (
            '{"n_total": NaN, "n_included": 1, "n_excluded": 0, "n_unclear": 0, '
            '"decisions": [{"study_index": 1, "criteria": '
            '[{"id": "IC1", "label": "MET", "rationale": "ok"}, '
            '{"id": "EC1", "label": "NOT_TRIGGERED", "rationale": "ok"}], '
            '"final_decision": "INCLUDE"}]}'
        )
        with self.assertRaises(ValueError) as ctx:
            validate_gatekeeper_answer(raw, studies)
        self.assertIn("JSON", str(ctx.exception))

    def test_rejects_infinity_constant(self):
        studies = [_study()]
        raw = (
            '{"n_total": Infinity, "n_included": 1, "n_excluded": 0, "n_unclear": 0, '
            '"decisions": [{"study_index": 1, "criteria": '
            '[{"id": "IC1", "label": "MET", "rationale": "ok"}, '
            '{"id": "EC1", "label": "NOT_TRIGGERED", "rationale": "ok"}], '
            '"final_decision": "INCLUDE"}]}'
        )
        with self.assertRaises(ValueError) as ctx:
            validate_gatekeeper_answer(raw, studies)
        self.assertIn("JSON", str(ctx.exception))

    def test_rejects_invalid_final_decision_value(self):
        studies = [_study()]
        bad = _mutate_answer(
            studies,
            lambda payload: payload["decisions"][0].__setitem__(
                "final_decision", "MAYBE"
            ),
        )
        with self.assertRaises(ValueError) as ctx:
            validate_gatekeeper_answer(bad, studies)
        self.assertIn("Invalid final_decision value", str(ctx.exception))

    def test_rejects_final_decision_inconsistent_with_criteria(self):
        studies = [_study()]
        payload = json.loads(_answer(studies, decision="EXCLUDE"))
        payload["decisions"][0]["final_decision"] = "INCLUDE"
        payload["n_included"] = 1
        payload["n_excluded"] = 0
        payload["n_unclear"] = 0
        with self.assertRaises(ValueError) as ctx:
            validate_gatekeeper_answer(json.dumps(payload), studies)
        self.assertIn("does not match get_final_decision rules", str(ctx.exception))

    def test_rejects_count_mismatch(self):
        studies = [_study()]
        bad = _mutate_answer(
            studies,
            lambda payload: payload.__setitem__("n_included", 0),
        )
        with self.assertRaises(ValueError) as ctx:
            validate_gatekeeper_answer(bad, studies)
        self.assertIn("n_included", str(ctx.exception))

    def test_rejects_unexpected_root_attribute(self):
        studies = [_study()]
        bad = _mutate_answer(
            studies,
            lambda payload: payload.__setitem__("extra", True),
        )
        with self.assertRaises(ValueError) as ctx:
            validate_gatekeeper_answer(bad, studies)
        self.assertIn("Unexpected root attributes", str(ctx.exception))

    def test_rejects_unexpected_study_index(self):
        studies = [_study(1)]
        bad = _mutate_answer(
            studies,
            lambda payload: payload["decisions"][0].__setitem__("study_index", 99),
        )
        with self.assertRaises(ValueError) as ctx:
            validate_gatekeeper_answer(bad, studies)
        self.assertIn("Unexpected study_index", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
