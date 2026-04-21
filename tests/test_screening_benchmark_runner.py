import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from bastirr.benchmarking.model_presets import ResolvedModelPreset
from bastirr.benchmarking.review_suites import ScreeningBenchmarkReview
from bastirr.benchmarking.runner import _aggregate_runs, run_screening_benchmark


class _ResolvedPresetWrapper:
    def __init__(self, resolved_preset):
        self._resolved_preset = resolved_preset

    def resolve(self):
        return self._resolved_preset


class ScreeningBenchmarkRunnerTests(unittest.TestCase):
    def test_run_screening_benchmark_writes_summary_files(self):
        review_case = ScreeningBenchmarkReview(
            key="synthetic_review",
            split="val",
            review_url="https://example.test/review",
            title="Synthetic Review",
            expected_n_studies=10,
            expected_n_screen_pass=6,
            expected_n_screen_exclude=4,
        )
        gatekeeper_model = ResolvedModelPreset(
            key="ollama_qwen3_5_27b_bf16",
            description="Ollama via OpenAI-compatible API",
            display_name="qwen3.5:27b-bf16",
            backend="openai",
            model_id="qwen3.5:27b-bf16",
            api_base="http://localhost:11434/v1",
            api_key="ollama",
            api_key_source="OPENAI_API_KEY",
        )
        orchestrator_model = ResolvedModelPreset(
            key="openai_gpt5",
            description="OpenAI API",
            display_name="gpt-5",
            backend="openai",
            model_id="gpt-5",
            api_base=None,
            api_key="test-key",
            api_key_source="OPENAI_API_KEY",
        )
        synthetic_metrics = {
            "benchmark_run_id": "synthetic_review_ollama_qwen3_5_27b_bf16_fixed_openai_gpt5_run1",
            "suite": "screening_ladder",
            "gold_label_policy": "exclude_label_0_5",
            "gold_label_policy_description": (
                "dataset label 1.0 counts as INCLUDE; 0.5 and 0.0 count as EXCLUDE"
            ),
            "review_key": review_case.key,
            "review_title": review_case.title,
            "review_url": review_case.review_url,
            "split": review_case.split,
            "run_index": 1,
            "run_status": "completed",
            "error": "",
            "screening_completion_status": "complete",
            "scored_for_aggregate": True,
            "screening_attempt_count": 1,
            "rerun_triggered": False,
            "incomplete_reason": "",
            "duration_seconds": 1.5,
            "run_dir": "/tmp/synthetic",
            "gatekeeper_preset": gatekeeper_model.key,
            "gatekeeper_model_label": gatekeeper_model.model_label,
            "gatekeeper_backend": gatekeeper_model.backend,
            "gatekeeper_model_id": gatekeeper_model.model_id,
            "gatekeeper_api_base": gatekeeper_model.api_base,
            "gatekeeper_api_key_source": gatekeeper_model.api_key_source,
            "orchestrator_policy": "fixed",
            "orchestrator_preset": orchestrator_model.key,
            "orchestrator_model_label": orchestrator_model.model_label,
            "orchestrator_backend": orchestrator_model.backend,
            "orchestrator_model_id": orchestrator_model.model_id,
            "orchestrator_api_base": "",
            "orchestrator_api_key_source": orchestrator_model.api_key_source,
            "n_studies": 10,
            "gold_pass_count": 6,
            "gold_exclude_count": 4,
            "predicted_pass_count": 5,
            "predicted_exclude_count": 5,
            "screening_decision_count": 10,
            "missing_decision_count": 0,
            "duplicate_decision_count": 0,
            "invalid_decision_count": 0,
            "decision_coverage": 1.0,
            "parse_success": True,
            "tp": 5,
            "fp": 0,
            "tn": 4,
            "fn": 1,
            "accuracy": 0.9,
            "precision": 1.0,
            "recall": 5 / 6,
            "specificity": 1.0,
            "f1": 10 / 11,
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            experiment_dir = Path(tmpdir) / "benchmark"
            experiment_dir.mkdir(parents=True, exist_ok=True)

            with patch(
                "bastirr.benchmarking.runner._experiment_root",
                return_value=experiment_dir,
            ), patch(
                "bastirr.benchmarking.runner.resolve_review_selection",
                return_value=[review_case],
            ), patch(
                "bastirr.benchmarking.runner.resolve_model_presets",
                return_value=[gatekeeper_model],
            ), patch(
                "bastirr.benchmarking.runner.get_model_preset",
                return_value=_ResolvedPresetWrapper(orchestrator_model),
            ), patch(
                "bastirr.benchmarking.runner.run_screening_review",
                return_value=synthetic_metrics,
            ):
                actual_dir, summary = run_screening_benchmark(
                    suite_name="screening_ladder",
                    model_presets=["ollama_qwen3_5_27b_bf16"],
                    repeats=1,
                    orchestrator_policy="fixed",
                    orchestrator_model_key="openai_gpt5",
                    review_keys=[review_case.key],
                    gold_label_policy="exclude_label_0_5",
                )

            self.assertEqual(actual_dir, experiment_dir)
            self.assertEqual(len(summary["runs"]), 1)
            self.assertTrue((experiment_dir / "summary.json").exists())
            self.assertTrue((experiment_dir / "summary.csv").exists())
            self.assertTrue((experiment_dir / "leaderboard.md").exists())
            self.assertTrue((experiment_dir / "review_leaderboard.md").exists())

            with open(experiment_dir / "summary.csv", "r", encoding="utf-8") as f:
                csv_header = f.readline().strip().split(",")

            with open(experiment_dir / "summary.json", "r", encoding="utf-8") as f:
                payload = json.load(f)
            self.assertEqual(csv_header[0], "benchmark_run_id")
            self.assertEqual(csv_header[1], "suite")
            self.assertEqual(csv_header[2], "review_key")
            self.assertEqual(payload["runs"][0]["review_key"], review_case.key)
            self.assertEqual(payload["gold_label_policy"], "exclude_label_0_5")
            self.assertTrue(payload["runs"][0]["scored_for_aggregate"])
            self.assertEqual(payload["leaderboard"][0]["gatekeeper_preset"], gatekeeper_model.key)
            self.assertEqual(
                payload["review_leaderboard"][0]["review_key"],
                review_case.key,
            )
            self.assertEqual(
                payload["review_leaderboard"][0]["gold_label_policy"],
                "exclude_label_0_5",
            )
            self.assertEqual(
                payload["leaderboard"][0]["gatekeeper_model_label"],
                gatekeeper_model.model_label,
            )

    def test_aggregate_runs_excludes_incomplete_runs_from_metric_means(self):
        complete_row = {
            "gold_label_policy": "exclude_label_0_5",
            "gatekeeper_preset": "openai_gpt5",
            "gatekeeper_model_label": "gpt-5",
            "gatekeeper_backend": "openai",
            "gatekeeper_api_base": "",
            "orchestrator_policy": "fixed",
            "orchestrator_preset": "openai_gpt5",
            "orchestrator_model_label": "gpt-5",
            "orchestrator_backend": "openai",
            "orchestrator_api_base": "",
            "review_key": "review_a",
            "run_status": "completed",
            "parse_success": True,
            "decision_coverage": 1.0,
            "accuracy": 0.9,
            "precision": 1.0,
            "recall": 0.8,
            "specificity": 1.0,
            "f1": 0.888,
            "duration_seconds": 10.0,
            "scored_for_aggregate": True,
        }
        incomplete_row = {
            **complete_row,
            "review_key": "review_b",
            "run_status": "incomplete",
            "parse_success": False,
            "decision_coverage": 0.025,
            "accuracy": 0.995,
            "precision": 1.0,
            "recall": 0.8,
            "specificity": 1.0,
            "f1": 0.888,
            "duration_seconds": 12.0,
            "scored_for_aggregate": False,
        }

        aggregates = _aggregate_runs([complete_row, incomplete_row])

        self.assertEqual(len(aggregates), 1)
        aggregate = aggregates[0]
        self.assertEqual(aggregate["n_runs"], 2)
        self.assertEqual(aggregate["n_scored_runs"], 1)
        self.assertEqual(aggregate["n_incomplete_runs"], 1)
        self.assertEqual(aggregate["n_error_runs"], 0)
        self.assertAlmostEqual(aggregate["mean_f1"], complete_row["f1"])
        self.assertAlmostEqual(aggregate["mean_accuracy"], complete_row["accuracy"])
        self.assertAlmostEqual(aggregate["parse_success_rate"], 0.5)
