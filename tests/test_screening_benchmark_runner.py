import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from bastirr.benchmarking.backfill import backfill_policy_views
from bastirr.benchmarking.model_presets import ResolvedModelPreset
from bastirr.benchmarking.review_suites import ScreeningBenchmarkReview
from bastirr.benchmarking.runner import (
    _aggregate_runs,
    run_screening_benchmark,
)


class _ResolvedPresetWrapper:
    def __init__(self, resolved_preset):
        self._resolved_preset = resolved_preset

    def resolve(self):
        return self._resolved_preset


class ScreeningBenchmarkRunnerTests(unittest.TestCase):
    def test_run_screening_benchmark_writes_policy_outputs_only(self):
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
        synthetic_raw_run = {
            "suite_name": "screening_ladder",
            "review_case": review_case,
            "review": SimpleNamespace(
                title=review_case.title,
                review_url=review_case.review_url,
                selection_criteria="Synthetic criteria",
                studies=[],
            ),
            "screening_decisions": [{"study_index": 1, "decision": "INCLUDE", "reason": "Matches"}],
            "gatekeeper_model": gatekeeper_model,
            "orchestrator_model": orchestrator_model,
            "orchestrator_policy": "fixed",
            "run_index": 1,
            "duration_seconds": 1.5,
            "raw_run_dir": Path("/tmp/synthetic"),
            "run_status": "completed",
            "error": "",
            "screening_attempt_count": 1,
            "rerun_triggered": False,
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            experiment_dir = Path(tmpdir) / "benchmark"
            experiment_dir.mkdir(parents=True, exist_ok=True)
            policy_dir = experiment_dir / "exclude_policy"

            def _fake_materialize_policy_outputs(*args, **kwargs):
                policy_dir.mkdir(parents=True, exist_ok=True)
                (policy_dir / "runs").mkdir(parents=True, exist_ok=True)
                for name in ("summary.json", "summary.csv", "leaderboard.md", "review_leaderboard.md"):
                    (policy_dir / name).write_text("test\n", encoding="utf-8")
                return policy_dir, {"runs": [{"review_key": review_case.key, "scored_for_aggregate": True}]}

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
                return_value=synthetic_raw_run,
            ), patch(
                "bastirr.benchmarking.runner._materialize_policy_outputs",
                side_effect=_fake_materialize_policy_outputs,
            ), patch(
                "bastirr.benchmarking.runner.write_policy_eda_notebook",
                return_value={
                    "notebook_path": str(policy_dir / "screening_results_analysis.ipynb"),
                    "executed": False,
                    "execution_error": "",
                },
            ), patch(
                "bastirr.benchmarking.runner.write_policy_html_report",
                return_value={
                    "report_path": str(policy_dir / "screening_results_summary.html"),
                    "title": "Title and Abstract Screening Benchmark Summary",
                },
            ), patch(
                "bastirr.benchmarking.runner.write_policy_comparison_report",
                return_value={
                    "report_path": str(experiment_dir / "screening_policy_comparison.html"),
                    "title": "Screening Benchmark Policy Comparison",
                },
            ):
                actual_dir, summary = run_screening_benchmark(
                    suite_name="screening_ladder",
                    model_presets=["ollama_qwen3_5_27b_bf16"],
                    repeats=1,
                    orchestrator_policy="fixed",
                    orchestrator_model_key="openai_gpt5",
                    review_keys=[review_case.key],
                    gold_label_policies=["exclude_label_0_5"],
                )

            self.assertEqual(actual_dir, experiment_dir)
            self.assertFalse((experiment_dir / "summary.json").exists())
            self.assertFalse((experiment_dir / "summary.csv").exists())
            self.assertFalse((experiment_dir / "leaderboard.md").exists())
            self.assertFalse((experiment_dir / "review_leaderboard.md").exists())
            self.assertFalse((experiment_dir / "runs").exists())
            self.assertTrue((policy_dir / "summary.json").exists())
            self.assertTrue((policy_dir / "summary.csv").exists())
            self.assertTrue((policy_dir / "leaderboard.md").exists())
            self.assertTrue((policy_dir / "review_leaderboard.md").exists())

            self.assertEqual(summary["suite"], "screening_ladder")
            self.assertEqual(summary["gold_label_policies"], ["exclude_label_0_5"])
            self.assertIn("exclude_label_0_5", summary["policy_outputs"])
            self.assertEqual(
                summary["policy_outputs"]["exclude_label_0_5"]["directory"],
                str(policy_dir),
            )
            self.assertEqual(
                summary["policy_outputs"]["exclude_label_0_5"]["eda_notebook"],
                str(policy_dir / "screening_results_analysis.ipynb"),
            )
            self.assertEqual(
                summary["policy_outputs"]["exclude_label_0_5"]["html_report"],
                str(policy_dir / "screening_results_summary.html"),
            )
            self.assertEqual(summary["raw_runs_dir"], str(experiment_dir / "_raw_runs"))
            self.assertTrue((experiment_dir / "_raw_runs").exists())
            self.assertTrue((experiment_dir / "benchmark_checkpoint.json").exists())
            self.assertIsNone(summary["comparison_html_report"])

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

    def test_backfill_policy_views_restructures_flat_benchmark_directory(self):
        review_case = ScreeningBenchmarkReview(
            key="synthetic_review",
            split="val",
            review_url="https://example.test/review",
            title="Synthetic Review",
            expected_n_studies=2,
            expected_n_screen_pass=1,
            expected_n_screen_exclude=1,
        )
        gatekeeper_model = ResolvedModelPreset(
            key="openai_gpt5",
            description="OpenAI API",
            display_name="gpt-5",
            backend="openai",
            model_id="gpt-5",
            api_base=None,
            api_key="test-key",
            api_key_source="OPENAI_API_KEY",
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            experiment_dir = Path(tmpdir) / "benchmark"
            run_dir = experiment_dir / "runs" / "synthetic_review_openai_gpt5_fixed_openai_gpt5_run1"
            run_dir.mkdir(parents=True, exist_ok=True)

            (experiment_dir / "summary.json").write_text(json.dumps({
                "suite": "screening_ladder",
                "repeats": 1,
                "review_keys": [review_case.key],
                "model_presets": ["openai_gpt5"],
                "orchestrator_policy": "fixed",
                "orchestrator_preset": "openai_gpt5",
            }), encoding="utf-8")
            for filename in ("summary.csv", "leaderboard.md", "review_leaderboard.md"):
                (experiment_dir / filename).write_text("legacy\n", encoding="utf-8")

            (run_dir / "workflow.log").write_text("workflow\n", encoding="utf-8")
            (run_dir / "activity.md").write_text("activity\n", encoding="utf-8")
            (run_dir / "screening_inspection.json").write_text("{}\n", encoding="utf-8")
            (run_dir / "screening_inspection.md").write_text("inspection\n", encoding="utf-8")
            (run_dir / "evidence.json").write_text(json.dumps({
                "screening_decisions": [
                    {"study_index": 1, "decision": "INCLUDE", "reason": "Matches"},
                    {"study_index": 2, "decision": "EXCLUDE", "reason": "No match"},
                ]
            }), encoding="utf-8")
            (run_dir / "metrics.json").write_text(json.dumps({
                "review_key": review_case.key,
                "gatekeeper_preset": "openai_gpt5",
                "orchestrator_preset": "openai_gpt5",
                "orchestrator_policy": "fixed",
                "run_index": 1,
                "duration_seconds": 1.5,
                "run_status": "completed",
                "error": "",
            }), encoding="utf-8")

            def _fake_materialize_policy_outputs(
                experiment_dir_arg,
                *,
                label_policy,
                **_kwargs,
            ):
                policy_dir = experiment_dir_arg / (
                    "include_policy" if label_policy == "include_label_0_5" else "exclude_policy"
                )
                (policy_dir / "runs").mkdir(parents=True, exist_ok=True)
                for filename in ("summary.json", "summary.csv", "leaderboard.md", "review_leaderboard.md"):
                    (policy_dir / filename).write_text("policy\n", encoding="utf-8")
                return policy_dir, {"gold_label_policy": label_policy}

            with patch(
                "bastirr.benchmarking.backfill.resolve_review_selection",
                return_value=[review_case],
            ), patch(
                "bastirr.benchmarking.backfill.load_review",
                return_value=SimpleNamespace(title=review_case.title, review_url=review_case.review_url),
            ), patch(
                "bastirr.benchmarking.backfill.get_model_preset",
                return_value=_ResolvedPresetWrapper(gatekeeper_model),
            ), patch(
                "bastirr.benchmarking.backfill._materialize_policy_outputs",
                side_effect=_fake_materialize_policy_outputs,
            ), patch(
                "bastirr.benchmarking.backfill.write_policy_eda_notebook",
                return_value={
                    "notebook_path": str(experiment_dir / "include_policy" / "screening_results_analysis.ipynb"),
                    "executed": False,
                    "execution_error": "",
                },
            ), patch(
                "bastirr.benchmarking.backfill.write_policy_html_report",
                return_value={
                    "report_path": str(experiment_dir / "include_policy" / "screening_results_summary.html"),
                    "title": "Title and Abstract Screening Benchmark Summary",
                },
            ), patch(
                "bastirr.benchmarking.backfill.write_policy_comparison_report",
                return_value={
                    "report_path": str(experiment_dir / "screening_policy_comparison.html"),
                    "title": "Screening Benchmark Policy Comparison",
                },
            ):
                result = backfill_policy_views(experiment_dir)

            self.assertTrue((experiment_dir / "include_policy").exists())
            self.assertTrue((experiment_dir / "exclude_policy").exists())
            self.assertFalse((experiment_dir / "summary.json").exists())
            self.assertFalse((experiment_dir / "summary.csv").exists())
            self.assertFalse((experiment_dir / "leaderboard.md").exists())
            self.assertFalse((experiment_dir / "review_leaderboard.md").exists())
            self.assertFalse((experiment_dir / "runs").exists())
            self.assertIn("include_label_0_5", result["policies"])
            self.assertIn("exclude_label_0_5", result["policies"])
            self.assertIn("eda_notebook", result["policies"]["include_label_0_5"])
            self.assertIn("html_report", result["policies"]["include_label_0_5"])
            self.assertEqual(
                result["comparison_html_report"],
                str(experiment_dir / "screening_policy_comparison.html"),
            )
