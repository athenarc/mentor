"""Tests for bulk screening benchmark runner, backfill, and summary aggregation."""

import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from experiments.harness.backfill import (
    _restore_missing_policy_trace_files,
    _snapshot_policy_trace_files,
    backfill_policy_views,
    _load_checkpoint_raw_runs,
)
from experiments.harness.model_presets import ResolvedModelPreset
from experiments.harness.review_suites import ScreeningBenchmarkReview
from experiments.harness.runner import (
    _aggregate_runs,
    _link_or_copy,
    _write_summary_csv,
    rerun_screening_reviews_in_experiment,
    run_screening_benchmark,
)


class _ResolvedPresetWrapper:
    def __init__(self, resolved_preset):
        self._resolved_preset = resolved_preset

    def resolve(self):
        return self._resolved_preset


class ScreeningBenchmarkRunnerTests(unittest.TestCase):
    def test_link_or_copy_noops_when_source_and_destination_are_same_path(self):
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as tmpdir:
            path = Path(tmpdir) / "trace.log"
            path.write_text("trace", encoding="utf-8")

            _link_or_copy(path, path)

            self.assertEqual(path.read_text(encoding="utf-8"), "trace")

    def test_link_or_copy_noops_when_absolute_and_relative_paths_match(self):
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as tmpdir:
            path = Path(tmpdir) / "trace.log"
            path.write_text("trace", encoding="utf-8")
            relative_path = path.resolve().relative_to(Path.cwd().resolve())

            _link_or_copy(path.resolve(), relative_path)

            self.assertEqual(path.read_text(encoding="utf-8"), "trace")

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
            include_policy_dir = experiment_dir / "include_policy"
            exclude_policy_dir = experiment_dir / "exclude_policy"

            def _fake_materialize_policy_outputs(*args, **kwargs):
                policy_dir = (
                    include_policy_dir
                    if kwargs["label_policy"] == "include_label_0_5"
                    else exclude_policy_dir
                )
                policy_dir.mkdir(parents=True, exist_ok=True)
                (policy_dir / "runs").mkdir(parents=True, exist_ok=True)
                for name in ("summary.json", "summary.csv", "leaderboard.md", "review_leaderboard.md"):
                    (policy_dir / name).write_text("test\n", encoding="utf-8")
                return policy_dir, {
                    "gold_label_policy": kwargs["label_policy"],
                    "runs": [{"review_key": review_case.key, "scored_for_aggregate": True}],
                }

            with patch(
                "experiments.harness.runner._experiment_root",
                return_value=experiment_dir,
            ), patch(
                "experiments.harness.runner.resolve_review_selection",
                return_value=[review_case],
            ), patch(
                "experiments.harness.runner.resolve_model_presets",
                return_value=[gatekeeper_model],
            ), patch(
                "experiments.harness.runner.get_model_preset",
                return_value=_ResolvedPresetWrapper(orchestrator_model),
            ), patch(
                "experiments.harness.runner.run_screening_review",
                return_value=synthetic_raw_run,
            ), patch(
                "experiments.harness.runner._materialize_policy_outputs",
                side_effect=_fake_materialize_policy_outputs,
            ), patch(
                "experiments.harness.runner.write_policy_eda_notebook",
                return_value={
                    "notebook_path": "screening_results_analysis.ipynb",
                    "executed": False,
                    "execution_error": "",
                },
            ), patch(
                "experiments.harness.runner.write_policy_html_report",
                return_value={
                    "report_path": "screening_results_summary.html",
                    "title": "Title and Abstract Screening Benchmark Summary",
                },
            ), patch(
                "experiments.harness.runner.write_policy_comparison_report",
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
                )

            self.assertEqual(actual_dir, experiment_dir)
            self.assertFalse((experiment_dir / "summary.json").exists())
            self.assertFalse((experiment_dir / "summary.csv").exists())
            self.assertFalse((experiment_dir / "leaderboard.md").exists())
            self.assertFalse((experiment_dir / "review_leaderboard.md").exists())
            self.assertFalse((experiment_dir / "runs").exists())
            for policy_dir in (include_policy_dir, exclude_policy_dir):
                self.assertTrue((policy_dir / "summary.json").exists())
                self.assertTrue((policy_dir / "summary.csv").exists())
                self.assertTrue((policy_dir / "leaderboard.md").exists())
                self.assertTrue((policy_dir / "review_leaderboard.md").exists())

            self.assertEqual(summary["suite"], "screening_ladder")
            self.assertEqual(summary["gold_label_policies"], ["include_label_0_5", "exclude_label_0_5"])
            self.assertIn("include_label_0_5", summary["policy_outputs"])
            self.assertIn("exclude_label_0_5", summary["policy_outputs"])
            self.assertEqual(
                summary["policy_outputs"]["exclude_label_0_5"]["directory"],
                str(exclude_policy_dir),
            )
            self.assertEqual(summary["raw_runs_dir"], str(experiment_dir / "_raw_runs"))
            self.assertTrue((experiment_dir / "_raw_runs").exists())
            self.assertTrue((experiment_dir / "benchmark_checkpoint.json").exists())
            self.assertEqual(
                summary["comparison_html_report"],
                str(experiment_dir / "screening_policy_comparison.html"),
            )

    def test_rerun_screening_benchmark_replaces_selected_review_from_policy_layout(self):
        review_a = ScreeningBenchmarkReview(
            key="review_a",
            split="val",
            review_url="https://example.test/review-a",
            title="Review A",
            expected_n_studies=2,
            expected_n_screen_pass=1,
            expected_n_screen_exclude=1,
        )
        review_b = ScreeningBenchmarkReview(
            key="review_b",
            split="val",
            review_url="https://example.test/review-b",
            title="Review B",
            expected_n_studies=2,
            expected_n_screen_pass=1,
            expected_n_screen_exclude=1,
        )
        model = ResolvedModelPreset(
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
            include_runs_dir = experiment_dir / "include_policy" / "runs"
            include_runs_dir.mkdir(parents=True, exist_ok=True)
            run_rows = []
            for review_case, reason in ((review_a, "old a"), (review_b, "old b")):
                run_id = f"{review_case.key}_openai_gpt5_fixed_openai_gpt5_run1"
                run_dir = include_runs_dir / run_id
                run_dir.mkdir(parents=True, exist_ok=True)
                (run_dir / "evidence.json").write_text(json.dumps({
                    "screening_decisions": [
                        {"study_index": 1, "decision": "INCLUDE", "reason": reason},
                        {"study_index": 2, "decision": "EXCLUDE", "reason": reason},
                    ]
                }), encoding="utf-8")
                metrics = {
                    "benchmark_run_id": run_id,
                    "suite": "screening_ladder",
                    "review_key": review_case.key,
                    "review_title": review_case.title,
                    "review_url": review_case.review_url,
                    "split": review_case.split,
                    "gatekeeper_preset": "openai_gpt5",
                    "orchestrator_preset": "openai_gpt5",
                    "orchestrator_policy": "fixed",
                    "run_index": 1,
                    "duration_seconds": 1.0,
                    "run_status": "completed",
                    "error": "",
                    "run_dir": str(run_dir),
                }
                (run_dir / "metrics.json").write_text(json.dumps(metrics), encoding="utf-8")
                run_rows.append(metrics)
            (experiment_dir / "include_policy" / "summary.json").write_text(json.dumps({
                "suite": "screening_ladder",
                "repeats": 1,
                "review_keys": ["review_a", "review_b"],
                "model_presets": ["openai_gpt5"],
                "orchestrator_policy": "fixed",
                "orchestrator_preset": "openai_gpt5",
                "gold_label_policy": "include_label_0_5",
                "runs": run_rows,
            }), encoding="utf-8")

            new_raw_dir = experiment_dir / "_raw_runs" / "review_b_openai_gpt5_fixed_openai_gpt5_run1"
            new_raw_run = {
                "suite_name": "screening_ladder",
                "review_case": review_b,
                "review": SimpleNamespace(
                    title=review_b.title,
                    review_url=review_b.review_url,
                    selection_criteria="Synthetic criteria",
                    studies=[],
                ),
                "screening_decisions": [
                    {"study_index": 1, "decision": "INCLUDE", "reason": "new b"},
                    {"study_index": 2, "decision": "EXCLUDE", "reason": "new b"},
                ],
                "gatekeeper_model": model,
                "orchestrator_model": model,
                "orchestrator_policy": "fixed",
                "run_index": 1,
                "duration_seconds": 2.0,
                "raw_run_dir": new_raw_dir,
                "run_status": "completed",
                "error": "",
                "screening_attempt_count": 1,
                "rerun_triggered": False,
                "benchmark_architecture": "batch_orchestrator_v1",
                "telemetry": {},
            }
            captured = {}

            def _fake_checkpoint_policy_outputs(_experiment_dir, **kwargs):
                captured["raw_runs"] = kwargs["raw_runs"]
                return {
                    label_policy: {
                        "directory": str(_experiment_dir / (
                            "include_policy" if label_policy == "include_label_0_5" else "exclude_policy"
                        )),
                        "summary": {"gold_label_policy": label_policy},
                    }
                    for label_policy in kwargs["selected_label_policies"]
                }

            rerun_kwargs = {}

            def _fake_run_screening_review(**kwargs):
                rerun_kwargs.update(kwargs)
                return new_raw_run

            def _fake_resolve_review_selection(_suite_name, review_keys=None):
                reviews = [review_a, review_b]
                if review_keys is None:
                    return reviews
                selected = set(review_keys)
                return [review for review in reviews if review.key in selected]

            with patch(
                "experiments.harness.runner.resolve_review_selection",
                side_effect=_fake_resolve_review_selection,
            ), patch(
                "experiments.harness.runner.load_review",
                return_value=SimpleNamespace(
                    title="Synthetic review",
                    review_url="https://example.test/review",
                    selection_criteria="Synthetic criteria",
                    studies=[],
                ),
            ), patch(
                "experiments.harness.runner.get_model_preset",
                return_value=_ResolvedPresetWrapper(model),
            ), patch(
                "experiments.harness.runner.run_screening_review",
                side_effect=_fake_run_screening_review,
            ), patch(
                "experiments.harness.runner._checkpoint_policy_outputs",
                side_effect=_fake_checkpoint_policy_outputs,
            ), patch(
                "experiments.harness.runner.write_policy_eda_notebook",
                return_value={"notebook_path": "", "executed": False, "execution_error": ""},
            ), patch(
                "experiments.harness.runner.write_policy_html_report",
                return_value={"report_path": "", "title": ""},
            ), patch(
                "experiments.harness.runner.write_policy_comparison_report",
                return_value={
                    "report_path": str(experiment_dir / "screening_policy_comparison.html"),
                    "title": "Screening Benchmark Policy Comparison",
                },
            ):
                _actual_dir, summary = rerun_screening_reviews_in_experiment(
                    experiment_dir=experiment_dir,
                    review_keys=["review_b"],
                    execute_policy_notebooks=False,
                    orchestrator_max_steps=30,
                )

            self.assertEqual(summary["rerun_review_keys"], ["review_b"])
            self.assertEqual(summary["orchestrator_max_steps"], 30)
            self.assertEqual(rerun_kwargs["orchestrator_max_steps"], 30)
            raw_runs_by_review = {
                raw_run["review_case"].key: raw_run
                for raw_run in captured["raw_runs"]
            }
            self.assertEqual(
                raw_runs_by_review["review_a"]["screening_decisions"][0]["reason"],
                "old a",
            )
            self.assertEqual(
                raw_runs_by_review["review_b"]["screening_decisions"][0]["reason"],
                "new b",
            )
            checkpoint = json.loads((experiment_dir / "benchmark_checkpoint.json").read_text())
            self.assertEqual(checkpoint["orchestrator_max_steps"], 30)

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

    def test_write_summary_csv_accepts_fields_added_after_first_row(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir)
            _write_summary_csv(output_dir, [
                {
                    "benchmark_run_id": "run1",
                    "review_key": "review_a",
                    "run_status": "completed",
                },
                {
                    "benchmark_run_id": "run2",
                    "review_key": "review_b",
                    "run_status": "completed",
                    "chunk_count": 4,
                    "chunk_sizes": [25, 25, 25, 25],
                },
            ])
            csv_text = (output_dir / "summary.csv").read_text(encoding="utf-8")
            header = csv_text.splitlines()[0]
            self.assertIn("chunk_count", header)
            self.assertIn("chunk_sizes", header)
            self.assertIn("run2", csv_text)

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
                "experiments.harness.backfill.resolve_review_selection",
                return_value=[review_case],
            ), patch(
                "experiments.harness.backfill.load_review",
                return_value=SimpleNamespace(title=review_case.title, review_url=review_case.review_url),
            ), patch(
                "experiments.harness.backfill.get_model_preset",
                return_value=_ResolvedPresetWrapper(gatekeeper_model),
            ), patch(
                "experiments.harness.backfill._materialize_policy_outputs",
                side_effect=_fake_materialize_policy_outputs,
            ), patch(
                "experiments.harness.backfill.write_policy_eda_notebook",
                return_value={
                    "notebook_path": str(experiment_dir / "include_policy" / "screening_results_analysis.ipynb"),
                    "executed": False,
                    "execution_error": "",
                },
            ), patch(
                "experiments.harness.backfill.write_policy_html_report",
                return_value={
                    "report_path": str(experiment_dir / "include_policy" / "screening_results_summary.html"),
                    "title": "Title and Abstract Screening Benchmark Summary",
                },
            ), patch(
                "experiments.harness.backfill.write_policy_comparison_report",
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

    def test_backfill_policy_views_repairs_checkpointed_single_policy_directory(self):
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
            exclude_run_dir = (
                experiment_dir
                / "exclude_policy"
                / "runs"
                / "synthetic_review_openai_gpt5_fixed_openai_gpt5_run1"
            )
            exclude_run_dir.mkdir(parents=True, exist_ok=True)
            (experiment_dir / "benchmark_checkpoint.json").write_text(json.dumps({
                "suite": "screening_ladder",
                "benchmark_architecture": "loop_chunk_orchestrator_v1",
                "repeats": 1,
                "review_keys": [review_case.key],
                "model_presets": ["openai_gpt5"],
                "orchestrator_policy": "fixed",
                "orchestrator_preset": "openai_gpt5",
                "gold_label_policies": ["exclude_label_0_5"],
                "completed_raw_run_count": 1,
                "total_expected_raw_runs": 1,
                "completed_runs": [{
                    "benchmark_run_id": "synthetic_review_openai_gpt5_fixed_openai_gpt5_run1",
                    "review_key": review_case.key,
                    "gatekeeper_preset": "openai_gpt5",
                    "orchestrator_policy": "fixed",
                    "orchestrator_preset": "openai_gpt5",
                    "run_index": 1,
                    "run_status": "completed",
                    "raw_run_dir": "/other/machine/path/missing",
                }],
                "comparison_html_report": None,
                "policy_outputs": {
                    "exclude_label_0_5": {
                        "directory": str(experiment_dir / "exclude_policy"),
                        "summary_json": str(experiment_dir / "exclude_policy" / "summary.json"),
                    }
                },
                "loop_mode": "chunked",
                "chunk_count": None,
                "chunk_size": None,
            }), encoding="utf-8")
            (experiment_dir / "exclude_policy" / "summary.json").write_text(json.dumps({
                "gold_label_policy": "exclude_label_0_5",
                "runs": [{
                    "benchmark_run_id": "synthetic_review_openai_gpt5_fixed_openai_gpt5_run1",
                    "review_key": review_case.key,
                    "scored_for_aggregate": True,
                }],
            }), encoding="utf-8")
            for filename in ("summary.csv", "leaderboard.md", "review_leaderboard.md"):
                (experiment_dir / "exclude_policy" / filename).write_text("exclude\n", encoding="utf-8")
            (exclude_run_dir / "workflow.log").write_text("workflow\n", encoding="utf-8")
            (exclude_run_dir / "activity.md").write_text("activity\n", encoding="utf-8")
            (exclude_run_dir / "evidence.json").write_text(json.dumps({
                "screening_decisions": [
                    {"study_index": 1, "decision": "INCLUDE", "reason": "Matches"},
                    {"study_index": 2, "decision": "EXCLUDE", "reason": "No match"},
                ]
            }), encoding="utf-8")
            (exclude_run_dir / "metrics.json").write_text(json.dumps({
                "review_key": review_case.key,
                "gatekeeper_preset": "openai_gpt5",
                "orchestrator_preset": "openai_gpt5",
                "orchestrator_policy": "fixed",
                "run_index": 1,
                "duration_seconds": 1.5,
                "run_status": "completed",
                "error": "",
                "benchmark_architecture": "loop_chunk_orchestrator_v1",
            }), encoding="utf-8")

            with patch(
                "experiments.harness.backfill.resolve_review_selection",
                return_value=[review_case],
            ), patch(
                "experiments.harness.backfill.load_review",
                return_value=SimpleNamespace(
                    title=review_case.title,
                    review_url=review_case.review_url,
                    selection_criteria="Synthetic criteria",
                    studies=[
                        SimpleNamespace(title="Included study", label=1.0),
                        SimpleNamespace(title="Excluded study", label=0.0),
                    ],
                ),
            ), patch(
                "experiments.harness.backfill.get_model_preset",
                return_value=_ResolvedPresetWrapper(gatekeeper_model),
            ), patch(
                "experiments.harness.backfill.write_policy_eda_notebook",
                return_value={
                    "notebook_path": str(experiment_dir / "include_policy" / "screening_results_analysis.ipynb"),
                    "executed": False,
                    "execution_error": "",
                },
            ), patch(
                "experiments.harness.backfill.write_policy_html_report",
                return_value={
                    "report_path": str(experiment_dir / "include_policy" / "screening_results_summary.html"),
                    "title": "Title and Abstract Screening Benchmark Summary",
                },
            ), patch(
                "experiments.harness.backfill.write_policy_comparison_report",
                return_value={
                    "report_path": str(experiment_dir / "screening_policy_comparison.html"),
                    "title": "Screening Benchmark Policy Comparison",
                },
            ):
                result = backfill_policy_views(
                    experiment_dir,
                    execute_policy_notebooks=False,
                )

            self.assertTrue((experiment_dir / "exclude_policy" / "summary.json").exists())
            self.assertTrue((experiment_dir / "include_policy" / "summary.json").exists())
            self.assertIn("include_label_0_5", result["materialized_policies"])
            self.assertIn("exclude_label_0_5", result["skipped_existing_policies"])
            checkpoint = json.loads((experiment_dir / "benchmark_checkpoint.json").read_text())
            self.assertEqual(
                checkpoint["gold_label_policies"],
                ["include_label_0_5", "exclude_label_0_5"],
            )
            self.assertIn("include_label_0_5", checkpoint["policy_outputs"])
            self.assertIn("exclude_label_0_5", checkpoint["policy_outputs"])
            self.assertEqual(
                checkpoint["comparison_html_report"],
                str(experiment_dir / "screening_policy_comparison.html"),
            )

    def test_checkpoint_backfill_marks_complete_evidence_only_raw_run_completed(self):
        review_case = ScreeningBenchmarkReview(
            key="synthetic_review",
            split="val",
            review_url="https://example.test/review",
            title="Synthetic Review",
            expected_n_studies=2,
            expected_n_screen_pass=1,
            expected_n_screen_exclude=1,
        )
        model = ResolvedModelPreset(
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
            raw_dir = (
                experiment_dir
                / "_raw_runs"
                / "20260619_000000_synthetic_review_openai_gpt5_fixed_openai_gpt5_run1"
            )
            raw_dir.mkdir(parents=True, exist_ok=True)
            (raw_dir / "evidence.json").write_text(json.dumps({
                "screening_decisions": [
                    {"study_index": 1, "decision": "INCLUDE", "reason": "Matches"},
                    {"study_index": 2, "decision": "EXCLUDE", "reason": "No match"},
                ]
            }), encoding="utf-8")
            checkpoint = {
                "suite": "screening_ladder",
                "benchmark_architecture": "loop_chunk_orchestrator_v1",
                "review_keys": [review_case.key],
                "model_presets": ["openai_gpt5"],
                "orchestrator_policy": "fixed",
                "orchestrator_preset": "openai_gpt5",
                "completed_runs": [{
                    "benchmark_run_id": "synthetic_review_openai_gpt5_fixed_openai_gpt5_run1",
                    "review_key": review_case.key,
                    "gatekeeper_preset": "openai_gpt5",
                    "orchestrator_policy": "fixed",
                    "orchestrator_preset": "openai_gpt5",
                    "run_index": 1,
                    "run_status": "incomplete",
                    "raw_run_dir": str(raw_dir),
                }],
            }

            with patch(
                "experiments.harness.backfill.resolve_review_selection",
                return_value=[review_case],
            ), patch(
                "experiments.harness.backfill.load_review",
                return_value=SimpleNamespace(
                    title=review_case.title,
                    review_url=review_case.review_url,
                    selection_criteria="Synthetic criteria",
                    studies=[
                        SimpleNamespace(title="Included study", label=1.0),
                        SimpleNamespace(title="Excluded study", label=0.0),
                    ],
                ),
            ), patch(
                "experiments.harness.backfill.get_model_preset",
                return_value=_ResolvedPresetWrapper(model),
            ):
                raw_runs = _load_checkpoint_raw_runs(
                    experiment_dir,
                    checkpoint=checkpoint,
                    selected_label_policies=["exclude_label_0_5"],
                )

            self.assertEqual(len(raw_runs), 1)
            self.assertEqual(raw_runs[0]["run_status"], "completed")

    def test_backfill_trace_snapshot_restores_only_missing_files(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            policy_dir = Path(tmpdir) / "include_policy"
            run_dir = policy_dir / "runs" / "review_model_run1"
            run_dir.mkdir(parents=True)
            (run_dir / "activity.md").write_text("old activity", encoding="utf-8")
            (run_dir / "workflow.log").write_text("old workflow", encoding="utf-8")

            snapshots = _snapshot_policy_trace_files(policy_dir)
            (run_dir / "activity.md").unlink()
            (run_dir / "workflow.log").write_text("new workflow", encoding="utf-8")

            _restore_missing_policy_trace_files(policy_dir, snapshots)

            self.assertEqual((run_dir / "activity.md").read_text(encoding="utf-8"), "old activity")
            self.assertEqual((run_dir / "workflow.log").read_text(encoding="utf-8"), "new workflow")
