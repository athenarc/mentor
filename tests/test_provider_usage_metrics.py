"""Provider usage extraction and safe step raw access."""

from __future__ import annotations

import unittest
from types import SimpleNamespace

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


if __name__ == "__main__":
    unittest.main()
