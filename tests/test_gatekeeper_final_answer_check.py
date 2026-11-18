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


def _answer(studies: list[dict], *, decision: str = "INCLUDE") -> str:
    included = sum(1 for _ in studies if decision == "INCLUDE")
    return json.dumps(
        {
            "n_total": len(studies),
            "n_included": included,
            "n_excluded": len(studies) - included,
            "decisions": [
                {
                    "study_index": study["study_index"],
                    "title": study["title"],
                    "decision": decision,
                    "confidence": "high",
                    "rationale": "ok",
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

    def test_rejects_non_string_answer(self):
        with self.assertRaises(ValueError) as ctx:
            validate_gatekeeper_answer({"n_total": 1}, [_study()])
        self.assertIn("JSON string", str(ctx.exception))

    def test_rejects_title_mismatch(self):
        studies = [_study(title="Expected")]
        bad = _mutate_answer(
            studies,
            lambda payload: payload["decisions"][0].__setitem__("title", "Wrong"),
        )
        with self.assertRaises(ValueError) as ctx:
            validate_gatekeeper_answer(bad, studies)
        self.assertIn("Title mismatch", str(ctx.exception))

    def test_rejects_missing_decision(self):
        studies = [_study(1), _study(2, title="Other")]
        partial = json.loads(_answer([studies[0]]))
        partial["n_total"] = 1
        with self.assertRaises(ValueError):
            validate_gatekeeper_answer(json.dumps(partial), studies)

    def test_rejects_duplicate_json_keys(self):
        studies = [_study()]
        raw = (
            '{"n_total": 1, "n_included": 1, "n_excluded": 0, '
            '"decisions": [{"study_index": 1, "title": "Example title", '
            '"decision": "INCLUDE", "confidence": "high", "rationale": "ok"}], '
            '"n_total": 2}'
        )
        with self.assertRaises(ValueError):
            validate_gatekeeper_answer(raw, studies)

    def test_rejects_nan_constant(self):
        studies = [_study()]
        raw = (
            '{"n_total": NaN, "n_included": 1, "n_excluded": 0, '
            '"decisions": [{"study_index": 1, "title": "Example title", '
            '"decision": "INCLUDE", "confidence": "high", "rationale": "ok"}]}'
        )
        with self.assertRaises(ValueError) as ctx:
            validate_gatekeeper_answer(raw, studies)
        self.assertIn("JSON", str(ctx.exception))

    def test_rejects_infinity_constant(self):
        studies = [_study()]
        raw = (
            '{"n_total": Infinity, "n_included": 1, "n_excluded": 0, '
            '"decisions": [{"study_index": 1, "title": "Example title", '
            '"decision": "INCLUDE", "confidence": "high", "rationale": "ok"}]}'
        )
        with self.assertRaises(ValueError) as ctx:
            validate_gatekeeper_answer(raw, studies)
        self.assertIn("JSON", str(ctx.exception))

    def test_rejects_invalid_decision_value(self):
        studies = [_study()]
        bad = _mutate_answer(
            studies,
            lambda payload: payload["decisions"][0].__setitem__("decision", "MAYBE"),
        )
        with self.assertRaises(ValueError) as ctx:
            validate_gatekeeper_answer(bad, studies)
        self.assertIn("Invalid decision value", str(ctx.exception))

    def test_rejects_invalid_confidence(self):
        studies = [_study()]
        bad = _mutate_answer(
            studies,
            lambda payload: payload["decisions"][0].__setitem__("confidence", "sure"),
        )
        with self.assertRaises(ValueError) as ctx:
            validate_gatekeeper_answer(bad, studies)
        self.assertIn("Invalid confidence value", str(ctx.exception))

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
