"""Provider usage extraction and safe step raw access."""

from __future__ import annotations

import unittest
from types import SimpleNamespace

from mentor.logging.activity import flatten_step_metrics, summarize_step_metrics
from mentor.logging.provider_usage import extract_call_usage, raw_completion_from_step


class ExtractCallUsageTests(unittest.TestCase):
    def test_reads_cost_and_provider_from_object_extras(self):
        usage = SimpleNamespace(model_extra={"cost": 0.12})
        raw = SimpleNamespace(
            usage=usage,
            provider="DeepInfra",
            model_extra={},
        )
        got = extract_call_usage(raw)
        self.assertEqual(got["cost"], 0.12)
        self.assertEqual(got["provider"], "DeepInfra")

    def test_falls_back_to_openrouter_provider_name(self):
        raw = {
            "usage": {"cost": 0.01},
            "openrouter_metadata": {"provider_name": "DeepInfra"},
        }
        got = extract_call_usage(raw)
        self.assertEqual(got["cost"], 0.01)
        self.assertEqual(got["provider"], "DeepInfra")

    def test_none_raw_is_safe(self):
        got = extract_call_usage(None)
        self.assertIsNone(got["cost"])
        self.assertIsNone(got["provider"])


class RawCompletionFromStepTests(unittest.TestCase):
    def test_missing_model_output_message_attribute(self):
        step = SimpleNamespace()
        self.assertIsNone(raw_completion_from_step(step))

    def test_none_model_output_message(self):
        step = SimpleNamespace(model_output_message=None)
        self.assertIsNone(raw_completion_from_step(step))

    def test_reads_raw_when_present(self):
        raw = SimpleNamespace(provider="DeepInfra")
        step = SimpleNamespace(model_output_message=SimpleNamespace(raw=raw))
        self.assertIs(raw_completion_from_step(step), raw)


class SummarizeStepMetricsTests(unittest.TestCase):
    def test_flattens_nested_steps_and_sums_own_call_metrics(self):
        steps = [
            {
                "agent": "orchestrator",
                "input_tokens": 100,
                "output_tokens": 10,
                "cost": 0.01,
                "provider": "DeepInfra",
                "duration": 160,
                "steps": [
                    {
                        "agent": "gatekeeper",
                        "input_tokens": 50,
                        "output_tokens": 5,
                        "cost": 0.02,
                        "provider": "DeepInfra",
                        "duration": 52,
                    },
                    {
                        "agent": "gatekeeper",
                        "input_tokens": 40,
                        "output_tokens": 4,
                        "cost": 0.03,
                        "provider": "Together",
                        "duration": 40,
                    },
                ],
            }
        ]
        flat = flatten_step_metrics(steps)
        self.assertEqual(len(flat), 3)
        self.assertNotIn("steps", flat[0])

        summary = summarize_step_metrics(steps)
        self.assertEqual(summary["n_calls"], 3)
        self.assertAlmostEqual(summary["cost"], 0.06)
        self.assertEqual(summary["input_tokens"], 190)
        self.assertEqual(summary["output_tokens"], 19)
        self.assertEqual(summary["providers"], ["DeepInfra", "Together"])


if __name__ == "__main__":
    unittest.main()
