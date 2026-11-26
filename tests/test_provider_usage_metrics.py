"""Provider usage extraction and safe step raw access."""

from __future__ import annotations

import unittest
from datetime import datetime
from types import SimpleNamespace

from mentor.logging.activity import (
    StepRecord,
    activity_summary_payload,
    flatten_step_metrics,
    merge_activity_summary_into_provider_usage,
    summarize_step_metrics,
    with_nested_steps,
)
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


def _leaf_metrics(
    *,
    agent: str,
    input_tokens: int,
    output_tokens: int,
    duration: float,
    cost: float,
    provider: str,
) -> dict:
    record = StepRecord(
        timestamp=datetime.now(),
        agent_name=agent,
        step_type="action",
        step_number=1,
        duration_seconds=duration,
        token_input=input_tokens,
        token_output=output_tokens,
        cost=cost,
        provider=provider,
    )
    return record.to_metrics()


class SelfTotalMetricsTests(unittest.TestCase):
    def test_leaf_has_usage_self_only(self):
        node = _leaf_metrics(
            agent="gatekeeper",
            input_tokens=50,
            output_tokens=5,
            duration=52,
            cost=0.02,
            provider="DeepInfra",
        )
        self.assertEqual(node["usage"]["self"]["duration"], 52)
        self.assertEqual(node["usage"]["self"]["input_tokens"], 50)
        self.assertEqual(node["usage"]["self"]["provider"], "DeepInfra")
        self.assertNotIn("total", node["usage"])
        self.assertNotIn("self", node)
        self.assertNotIn("total", node)
        self.assertNotIn("steps", node)

    def test_parent_usage_self_is_exclusive_total_is_wall(self):
        parent = _leaf_metrics(
            agent="orchestrator",
            input_tokens=100,
            output_tokens=10,
            duration=160,
            cost=0.01,
            provider="DeepInfra",
        )
        children = [
            _leaf_metrics(
                agent="gatekeeper",
                input_tokens=50,
                output_tokens=5,
                duration=52,
                cost=0.02,
                provider="DeepInfra",
            ),
            _leaf_metrics(
                agent="gatekeeper",
                input_tokens=40,
                output_tokens=4,
                duration=40,
                cost=0.03,
                provider="Together",
            ),
        ]
        nested = with_nested_steps(parent, children)
        self.assertAlmostEqual(nested["usage"]["self"]["duration"], 68.0)
        self.assertEqual(nested["usage"]["total"]["duration"], 160)
        self.assertEqual(nested["usage"]["total"]["input_tokens"], 190)
        self.assertEqual(nested["usage"]["total"]["output_tokens"], 19)
        self.assertAlmostEqual(nested["usage"]["total"]["cost"], 0.06)
        self.assertEqual(len(nested["steps"]), 2)
        self.assertNotIn("total", nested["steps"][0]["usage"])


class SummarizeStepMetricsTests(unittest.TestCase):
    def test_flattens_usage_self_bags_and_sums_own_call_metrics(self):
        parent = _leaf_metrics(
            agent="orchestrator",
            input_tokens=100,
            output_tokens=10,
            duration=160,
            cost=0.01,
            provider="DeepInfra",
        )
        steps = [
            with_nested_steps(
                parent,
                [
                    _leaf_metrics(
                        agent="gatekeeper",
                        input_tokens=50,
                        output_tokens=5,
                        duration=52,
                        cost=0.02,
                        provider="DeepInfra",
                    ),
                    _leaf_metrics(
                        agent="gatekeeper",
                        input_tokens=40,
                        output_tokens=4,
                        duration=40,
                        cost=0.03,
                        provider="Together",
                    ),
                ],
            )
        ]
        flat = flatten_step_metrics(steps)
        self.assertEqual(len(flat), 3)
        self.assertAlmostEqual(flat[0]["duration"], 68.0)
        self.assertNotIn("steps", flat[0])
        self.assertNotIn("usage", flat[0])

        summary = summarize_step_metrics(steps)
        self.assertEqual(summary["n_calls"], 3)
        self.assertAlmostEqual(summary["cost"], 0.06)
        self.assertEqual(summary["input_tokens"], 190)
        self.assertEqual(summary["output_tokens"], 19)
        self.assertAlmostEqual(summary["duration"], 160.0)
        self.assertEqual(summary["providers"], ["DeepInfra", "Together"])


class MergeActivitySummaryUsageTests(unittest.TestCase):
    def test_folds_cost_tokens_calls_and_providers(self):
        base = {
            "cost": 0.10,
            "input_tokens": 100,
            "output_tokens": 20,
            "duration": 12.0,
            "providers": ["OpenAI"],
            "n_calls": 3,
        }
        summary = {
            "n_calls": 2,
            "cost": 0.05,
            "input_tokens": 40,
            "output_tokens": 5,
            "providers": ["OpenAI", "DeepInfra"],
        }
        merged = merge_activity_summary_into_provider_usage(base, summary)
        self.assertAlmostEqual(merged["cost"], 0.15)
        self.assertEqual(merged["input_tokens"], 140)
        self.assertEqual(merged["output_tokens"], 25)
        self.assertEqual(merged["n_calls"], 5)
        self.assertEqual(merged["providers"], ["DeepInfra", "OpenAI"])
        # Step exclusive duration is not mixed with summary wall time.
        self.assertAlmostEqual(merged["duration"], 12.0)
        self.assertAlmostEqual(base["cost"], 0.10)

    def test_empty_summary_is_noop_copy(self):
        base = {"cost": 0.1, "n_calls": 1, "providers": ["OpenAI"]}
        merged = merge_activity_summary_into_provider_usage(base, {})
        self.assertEqual(merged, base)
        self.assertIsNot(merged, base)

    def test_activity_summary_payload_includes_skipped(self):
        payload = activity_summary_payload(
            skipped=True,
            summary_metrics={"n_calls": 0, "duration": 0.0},
        )
        self.assertEqual(
            payload,
            {"skipped": True, "n_calls": 0, "duration": 0.0},
        )


if __name__ == "__main__":
    unittest.main()
