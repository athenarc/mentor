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
from experiments.catalog import ResolvedModel
from experiments.suites.review_suites import ScreeningBenchmarkReview
from experiments.harness.runner import (
    _aggregate_runs,
    _link_or_copy,
    _write_summary_csv,
)


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
        )
        gatekeeper_model = ResolvedModel(
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
                return_value=SimpleNamespace(title="Synthetic Review", review_url=review_case.key),
            ), patch(
                "experiments.harness.backfill.resolve_model",
                return_value=gatekeeper_model,
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
        )
        gatekeeper_model = ResolvedModel(
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
                    title="Synthetic Review",
                    review_url=review_case.key,
                    selection_criteria="Synthetic criteria",
                    studies=[
                        SimpleNamespace(title="Included study", label=1.0),
                        SimpleNamespace(title="Excluded study", label=0.0),
                    ],
                ),
            ), patch(
                "experiments.harness.backfill.resolve_model",
                return_value=gatekeeper_model,
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
        )
        model = ResolvedModel(
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
                    title="Synthetic Review",
                    review_url=review_case.key,
                    selection_criteria="Synthetic criteria",
                    studies=[
                        SimpleNamespace(title="Included study", label=1.0),
                        SimpleNamespace(title="Excluded study", label=0.0),
                    ],
                ),
            ), patch(
                "experiments.harness.backfill.resolve_model",
                return_value=model,
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
