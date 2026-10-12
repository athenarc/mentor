import ast
import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from bastirr.benchmarking.loop_runner import (
    LOOP_CHUNK_BENCHMARK_ARCHITECTURE,
    LOOP_BENCHMARK_ARCHITECTURE,
    _chunk_indices,
    _experiment_model_suffix,
    _missing_study_indices,
    rerun_screening_loop_reviews_in_experiment,
    run_screening_loop_benchmark,
)
from bastirr.benchmarking.model_presets import ResolvedModelPreset
from bastirr.benchmarking.review_suites import ScreeningBenchmarkReview
from bastirr.benchmarking.telemetry import (
    collect_activity_telemetry,
    compute_rationale_metrics,
)
from bastirr.benchmarking.totals import (
    merge_canonical_sources,
    register_canonical_sources_from_experiment,
    size_band_for,
    write_canonical_sources,
    write_screening_totals,
)
from bastirr.tools.screening_benchmark_tools import (
    append_screening_chunk_decisions_json,
    append_screening_decision_json,
)
from bastirr.tools.search_tools import (
    get_candidate_studies_chunk_json,
    get_candidate_study_json,
    load_review_data,
)


class _ResolvedPresetWrapper:
    def __init__(self, resolved_preset):
        self._resolved_preset = resolved_preset

    def resolve(self):
        return self._resolved_preset


class AgentFactoryStructureTests(unittest.TestCase):
    def test_agent_factories_have_reachable_top_level_returns(self):
        agents_dir = Path(__file__).resolve().parents[1] / "bastirr" / "agents"

        for path in sorted(agents_dir.glob("*.py")):
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            for node in tree.body:
                if not (
                    isinstance(node, ast.FunctionDef)
                    and node.name.startswith("create_")
                    and node.name.endswith("_agent")
                ):
                    continue

                top_level_return_positions = [
                    index
                    for index, statement in enumerate(node.body)
                    if isinstance(statement, ast.Return)
                ]
                self.assertTrue(
                    top_level_return_positions,
                    f"{path.name}:{node.name} has no top-level return",
                )

                first_return_position = top_level_return_positions[0]
                trailing_statements = [
                    statement
                    for statement in node.body[first_return_position + 1:]
                    if not (
                        isinstance(statement, ast.Expr)
                        and isinstance(statement.value, ast.Constant)
                        and statement.value.value is None
                    )
                ]
                self.assertFalse(
                    trailing_statements,
                    f"{path.name}:{node.name} has unreachable code after return",
                )


class ScreeningLoopBenchmarkTests(unittest.TestCase):
    def test_get_candidate_study_json_returns_one_label_free_study(self):
        load_review_data(json.dumps({
            "title": "Review",
            "objective": "Objective",
            "background": "Background",
            "selection_criteria": "Criteria",
            "studies": [
                {"study_index": 1, "title": "A", "abstract": "Abstract A"},
                {"study_index": 2, "title": "B", "abstract": "Abstract B"},
            ],
        }))

        payload = json.loads(get_candidate_study_json(study_index=2))

        self.assertEqual(payload["title"], "Review")
        self.assertEqual(payload["selection_criteria"], "Criteria")
        self.assertEqual(payload["n_total"], 2)
        self.assertEqual(len(payload["studies"]), 1)
        self.assertEqual(payload["studies"][0]["study_index"], 2)
        self.assertEqual(payload["studies"][0]["title"], "B")
        self.assertNotIn("study", payload)
        self.assertNotIn("label", payload["studies"][0])

    def test_get_candidate_studies_chunk_json_returns_label_free_chunk(self):
        load_review_data(json.dumps({
            "title": "Review",
            "objective": "Objective",
            "background": "Background",
            "selection_criteria": "Criteria",
            "studies": [
                {"study_index": 1, "title": "A", "abstract": "Abstract A", "label": 1.0},
                {"study_index": 2, "title": "B", "abstract": "Abstract B", "label": 0.0},
                {"study_index": 3, "title": "C", "abstract": "Abstract C", "label": 0.5},
            ],
        }))

        payload = json.loads(get_candidate_studies_chunk_json(study_indices_json="[2, 3]"))

        self.assertEqual(payload["title"], "Review")
        self.assertEqual(payload["n_total"], 3)
        self.assertNotIn("chunk_study_indices", payload)
        self.assertEqual([study["study_index"] for study in payload["studies"]], [2, 3])
        self.assertEqual([study["title"] for study in payload["studies"]], ["B", "C"])
        self.assertNotIn("label", payload["studies"][0])

    def test_append_screening_decision_json_updates_evidence_and_progress(self):
        response = json.dumps({
            "n_total": 1,
            "n_included": 1,
            "n_excluded": 0,
            "decisions": [{
                "study_index": 1,
                "title": "A",
                "decision": "INCLUDE",
                "rationale": "Matches the eligible population.",
                "confidence": "high",
            }],
        })

        with tempfile.TemporaryDirectory() as tmpdir:
            append_screening_decision_json(
                screening_response=response,
                output_dir=tmpdir,
                expected_study_index=1,
                expected_n_studies=2,
            )
            evidence = json.loads((Path(tmpdir) / "evidence.json").read_text(encoding="utf-8"))
            progress = json.loads((Path(tmpdir) / "screening_progress.json").read_text(encoding="utf-8"))

            self.assertEqual(len(evidence["screening_decisions"]), 1)
            self.assertEqual(evidence["screening_decisions"][0]["reason"], "Matches the eligible population.")
            self.assertEqual(progress["completed_study_indices"], [1])
            self.assertEqual(progress["next_study_index"], 2)

            with self.assertRaises(ValueError):
                append_screening_decision_json(
                    screening_response=response,
                    output_dir=tmpdir,
                    expected_study_index=1,
                    expected_n_studies=2,
                )

    def test_append_screening_chunk_decisions_json_updates_evidence_and_progress(self):
        response = json.dumps({
            "n_total": 2,
            "n_included": 1,
            "n_excluded": 1,
            "decisions": [
                {
                    "study_index": 2,
                    "title": "B",
                    "decision": "INCLUDE",
                    "rationale": "Potentially eligible.",
                    "confidence": "medium",
                },
                {
                    "study_index": 3,
                    "title": "C",
                    "decision": "EXCLUDE",
                    "rationale": "Wrong population.",
                    "confidence": "high",
                },
            ],
        })

        with tempfile.TemporaryDirectory() as tmpdir:
            append_screening_chunk_decisions_json(
                screening_response=response,
                output_dir=tmpdir,
                expected_study_indices_json="[2, 3]",
                expected_n_studies=4,
            )
            evidence = json.loads((Path(tmpdir) / "evidence.json").read_text(encoding="utf-8"))
            progress = json.loads((Path(tmpdir) / "screening_progress.json").read_text(encoding="utf-8"))

            self.assertEqual([row["study_index"] for row in evidence["screening_decisions"]], [2, 3])
            self.assertEqual(progress["completed_study_indices"], [2, 3])
            self.assertEqual(progress["next_study_index"], 1)

            with self.assertRaises(ValueError):
                append_screening_chunk_decisions_json(
                    screening_response=response,
                    output_dir=tmpdir,
                    expected_study_indices_json="[2, 3]",
                    expected_n_studies=4,
                )

    def test_append_screening_decision_json_rejects_wrong_index(self):
        response = json.dumps({
            "decisions": [{"study_index": 2, "decision": "EXCLUDE", "rationale": "Wrong population."}],
        })

        with tempfile.TemporaryDirectory() as tmpdir:
            with self.assertRaises(ValueError):
                append_screening_decision_json(
                    screening_response=response,
                    output_dir=tmpdir,
                    expected_study_index=1,
                    expected_n_studies=2,
                )

    def test_missing_study_indices_support_resume(self):
        review = SimpleNamespace(studies=[object(), object(), object()])
        decisions = [{"study_index": 1, "decision": "INCLUDE"}, {"study_index": 3, "decision": "EXCLUDE"}]

        self.assertEqual(_missing_study_indices(review, decisions), [2])

    def test_chunk_indices_default_schedule_matches_size_bands(self):
        self.assertEqual([len(chunk) for chunk in _chunk_indices(list(range(1, 11)))], [10])
        self.assertEqual([len(chunk) for chunk in _chunk_indices(list(range(1, 26)))], [25])
        self.assertEqual([len(chunk) for chunk in _chunk_indices(list(range(1, 51)))], [25, 25])
        self.assertEqual([len(chunk) for chunk in _chunk_indices(list(range(1, 101)))], [25, 25, 25, 25])
        self.assertEqual([len(chunk) for chunk in _chunk_indices(list(range(1, 201)))], [34, 34, 33, 33, 33, 33])
        self.assertEqual([len(chunk) for chunk in _chunk_indices(list(range(1, 11)), chunk_size=4)], [4, 4, 2])

    def test_experiment_model_suffix_uses_model_key_for_single_model_runs(self):
        self.assertEqual(_experiment_model_suffix(["openai_gpt5"]), "openai_gpt5")
        self.assertEqual(_experiment_model_suffix(["openai_gpt5", "deepseek_v4_pro"]), "models2")

    def test_collect_activity_telemetry_and_rationale_metrics(self):
        activity_logger = SimpleNamespace(steps=[
            SimpleNamespace(
                agent_name="orchestrator",
                step_type="action",
                token_input=10,
                token_output=5,
                duration_seconds=1.0,
                error=None,
            ),
            SimpleNamespace(
                agent_name="gatekeeper",
                step_type="planning",
                token_input=20,
                token_output=7,
                duration_seconds=2.0,
                error="schema error",
            ),
        ])

        telemetry = collect_activity_telemetry(
            activity_logger,
            duration_seconds=9.0,
            n_studies=3,
            retry_count=1,
            resume_count=1,
        )
        rationale = compute_rationale_metrics([
            {"study_index": 1, "reason": "Same text"},
            {"study_index": 2, "reason": "Same   text"},
            {"study_index": 3, "reason": ""},
        ])

        self.assertEqual(telemetry["total_input_tokens"], 30)
        self.assertEqual(telemetry["total_output_tokens"], 12)
        self.assertEqual(telemetry["total_tokens"], 42)
        self.assertEqual(telemetry["orchestrator_step_count"], 1)
        self.assertEqual(telemetry["gatekeeper_step_count"], 1)
        self.assertEqual(telemetry["error_step_count"], 1)
        self.assertEqual(telemetry["duration_per_study_seconds"], 3.0)
        self.assertEqual(rationale["empty_rationale_count"], 1)
        self.assertEqual(rationale["duplicate_rationale_count"], 1)
        self.assertAlmostEqual(rationale["rationale_reuse_rate"], 1 / 3)

    def test_run_screening_loop_benchmark_wires_policy_outputs(self):
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
            "orchestrator_model": gatekeeper_model,
            "orchestrator_policy": "fixed",
            "run_index": 1,
            "duration_seconds": 1.5,
            "raw_run_dir": Path("/tmp/synthetic"),
            "run_status": "completed",
            "error": "",
            "screening_attempt_count": 1,
            "rerun_triggered": False,
            "benchmark_architecture": LOOP_BENCHMARK_ARCHITECTURE,
            "telemetry": {"total_tokens": 10, "total_steps": 2},
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
                return {
                    "exclude_label_0_5": {
                        "directory": str(policy_dir),
                        "summary_json": str(policy_dir / "summary.json"),
                        "summary_csv": str(policy_dir / "summary.csv"),
                        "leaderboard_markdown": str(policy_dir / "leaderboard.md"),
                        "review_leaderboard_markdown": str(policy_dir / "review_leaderboard.md"),
                        "runs_dir": str(policy_dir / "runs"),
                        "html_report": "",
                        "eda_notebook": "",
                        "eda_notebook_executed": False,
                        "eda_notebook_execution_error": "",
                        "summary": {"runs": [{"benchmark_architecture": LOOP_BENCHMARK_ARCHITECTURE}]},
                    }
                }

            with patch(
                "bastirr.benchmarking.loop_runner._loop_experiment_root_for_mode",
                return_value=experiment_dir,
            ), patch(
                "bastirr.benchmarking.loop_runner.resolve_review_selection",
                return_value=[review_case],
            ), patch(
                "bastirr.benchmarking.loop_runner.resolve_model_presets",
                return_value=[gatekeeper_model],
            ), patch(
                "bastirr.benchmarking.loop_runner.get_model_preset",
                return_value=_ResolvedPresetWrapper(gatekeeper_model),
            ), patch(
                "bastirr.benchmarking.loop_runner.run_screening_loop_review",
                return_value=synthetic_raw_run,
            ), patch(
                "bastirr.benchmarking.loop_runner._checkpoint_policy_outputs",
                side_effect=_fake_materialize_policy_outputs,
            ), patch(
                "bastirr.benchmarking.loop_runner.write_policy_eda_notebook",
                return_value={
                    "notebook_path": str(policy_dir / "screening_results_analysis.ipynb"),
                    "executed": False,
                    "execution_error": "",
                },
            ), patch(
                "bastirr.benchmarking.loop_runner.write_policy_html_report",
                return_value={
                    "report_path": str(policy_dir / "screening_results_summary.html"),
                    "title": "Title and Abstract Screening Benchmark Summary",
                },
            ), patch(
                "bastirr.benchmarking.loop_runner.write_policy_comparison_report",
                return_value={
                    "report_path": str(experiment_dir / "screening_policy_comparison.html"),
                    "title": "Screening Benchmark Policy Comparison",
                },
            ):
                actual_dir, summary = run_screening_loop_benchmark(
                    suite_name="screening_ladder",
                    model_presets=["openai_gpt5"],
                    repeats=1,
                    orchestrator_policy="fixed",
                    orchestrator_model_key="openai_gpt5",
                    review_keys=[review_case.key],
                    gold_label_policies=["exclude_label_0_5"],
                )

            self.assertEqual(actual_dir, experiment_dir)
            self.assertEqual(summary["benchmark_architecture"], LOOP_BENCHMARK_ARCHITECTURE)
            self.assertIn("exclude_label_0_5", summary["policy_outputs"])
            self.assertEqual(summary["raw_runs_dir"], str(experiment_dir / "_raw_runs"))
            self.assertTrue((experiment_dir / "benchmark_checkpoint.json").exists())

    def test_run_screening_loop_benchmark_checkpoints_after_each_review(self):
        review_cases = [
            ScreeningBenchmarkReview(
                key="synthetic_review_a",
                split="val",
                review_url="https://example.test/review-a",
                title="Synthetic Review A",
                expected_n_studies=2,
                expected_n_screen_pass=1,
                expected_n_screen_exclude=1,
            ),
            ScreeningBenchmarkReview(
                key="synthetic_review_b",
                split="val",
                review_url="https://example.test/review-b",
                title="Synthetic Review B",
                expected_n_studies=3,
                expected_n_screen_pass=1,
                expected_n_screen_exclude=2,
            ),
        ]
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
            experiment_dir.mkdir(parents=True, exist_ok=True)
            policy_dir = experiment_dir / "exclude_policy"
            checkpoint_lengths: list[int] = []

            def _fake_run_screening_loop_review(**kwargs):
                self.assertEqual(kwargs["output_root"], experiment_dir / "_raw_runs")
                review_case = kwargs["review_case"]
                return {
                    "suite_name": "screening_ladder",
                    "review_case": review_case,
                    "review": SimpleNamespace(
                        title=review_case.title,
                        review_url=review_case.review_url,
                        selection_criteria="Synthetic criteria",
                        studies=[object()] * review_case.expected_n_studies,
                    ),
                    "screening_decisions": [
                        {"study_index": 1, "decision": "INCLUDE", "reason": "Matches"}
                    ],
                    "gatekeeper_model": gatekeeper_model,
                    "orchestrator_model": gatekeeper_model,
                    "orchestrator_policy": "fixed",
                    "run_index": kwargs["run_index"],
                    "duration_seconds": 1.5,
                    "raw_run_dir": kwargs["output_root"] / review_case.key,
                    "run_status": "completed",
                    "error": "",
                    "screening_attempt_count": 1,
                    "rerun_triggered": False,
                    "benchmark_architecture": LOOP_BENCHMARK_ARCHITECTURE,
                    "telemetry": {},
                }

            def _fake_checkpoint_policy_outputs(*args, **kwargs):
                checkpoint_lengths.append(len(kwargs["raw_runs"]))
                policy_dir.mkdir(parents=True, exist_ok=True)
                (policy_dir / "runs").mkdir(parents=True, exist_ok=True)
                for name in ("summary.json", "summary.csv", "leaderboard.md", "review_leaderboard.md"):
                    (policy_dir / name).write_text("checkpoint\n", encoding="utf-8")
                return {
                    "exclude_label_0_5": {
                        "directory": str(policy_dir),
                        "summary_json": str(policy_dir / "summary.json"),
                        "summary_csv": str(policy_dir / "summary.csv"),
                        "leaderboard_markdown": str(policy_dir / "leaderboard.md"),
                        "review_leaderboard_markdown": str(policy_dir / "review_leaderboard.md"),
                        "runs_dir": str(policy_dir / "runs"),
                        "html_report": "",
                        "eda_notebook": "",
                        "eda_notebook_executed": False,
                        "eda_notebook_execution_error": "",
                        "summary": {"runs": [{"review_key": row["review_case"].key} for row in kwargs["raw_runs"]]},
                    }
                }

            with patch(
                "bastirr.benchmarking.loop_runner._loop_experiment_root_for_mode",
                return_value=experiment_dir,
            ), patch(
                "bastirr.benchmarking.loop_runner.resolve_review_selection",
                return_value=review_cases,
            ), patch(
                "bastirr.benchmarking.loop_runner.resolve_model_presets",
                return_value=[gatekeeper_model],
            ), patch(
                "bastirr.benchmarking.loop_runner.get_model_preset",
                return_value=_ResolvedPresetWrapper(gatekeeper_model),
            ), patch(
                "bastirr.benchmarking.loop_runner.run_screening_loop_review",
                side_effect=_fake_run_screening_loop_review,
            ), patch(
                "bastirr.benchmarking.loop_runner._checkpoint_policy_outputs",
                side_effect=_fake_checkpoint_policy_outputs,
            ), patch(
                "bastirr.benchmarking.loop_runner.write_policy_eda_notebook",
                return_value={
                    "notebook_path": str(policy_dir / "screening_results_analysis.ipynb"),
                    "executed": False,
                    "execution_error": "",
                },
            ), patch(
                "bastirr.benchmarking.loop_runner.write_policy_html_report",
                return_value={
                    "report_path": str(policy_dir / "screening_results_summary.html"),
                    "title": "Title and Abstract Screening Benchmark Summary",
                },
            ):
                _actual_dir, summary = run_screening_loop_benchmark(
                    suite_name="screening_ladder",
                    model_presets=["openai_gpt5"],
                    repeats=1,
                    orchestrator_policy="fixed",
                    orchestrator_model_key="openai_gpt5",
                    review_keys=[case.key for case in review_cases],
                    gold_label_policies=["exclude_label_0_5"],
                )

            self.assertEqual(checkpoint_lengths, [1, 2])
            self.assertEqual(summary["completed_raw_run_count"], 2)
            self.assertEqual(summary["total_expected_raw_runs"], 2)
            manifest = json.loads(
                (experiment_dir / "benchmark_checkpoint.json").read_text(encoding="utf-8")
            )
            self.assertEqual(manifest["completed_raw_run_count"], 2)
            self.assertEqual(manifest["raw_runs_dir"], str(experiment_dir / "_raw_runs"))

    def test_run_screening_loop_benchmark_chunked_mode_uses_chunk_runner(self):
        review_case = ScreeningBenchmarkReview(
            key="synthetic_review",
            split="val",
            review_url="https://example.test/review",
            title="Synthetic Review",
            expected_n_studies=50,
            expected_n_screen_pass=25,
            expected_n_screen_exclude=25,
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
        synthetic_raw_run = {
            "suite_name": "screening_ladder",
            "review_case": review_case,
            "review": SimpleNamespace(
                title=review_case.title,
                review_url=review_case.review_url,
                selection_criteria="Synthetic criteria",
                studies=[object()] * 50,
            ),
            "screening_decisions": [{"study_index": 1, "decision": "INCLUDE", "reason": "Matches"}],
            "gatekeeper_model": gatekeeper_model,
            "orchestrator_model": gatekeeper_model,
            "orchestrator_policy": "fixed",
            "run_index": 1,
            "duration_seconds": 1.5,
            "raw_run_dir": Path("/tmp/synthetic"),
            "run_status": "completed",
            "error": "",
            "screening_attempt_count": 1,
            "rerun_triggered": False,
            "benchmark_architecture": LOOP_CHUNK_BENCHMARK_ARCHITECTURE,
            "telemetry": {"chunk_count": 2, "chunk_sizes": [25, 25]},
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            experiment_dir = Path(tmpdir) / "benchmark"
            experiment_dir.mkdir(parents=True, exist_ok=True)
            policy_dir = experiment_dir / "exclude_policy"
            chunk_runner_kwargs = {}

            def _fake_chunk_runner(**kwargs):
                chunk_runner_kwargs.update(kwargs)
                return synthetic_raw_run

            def _fake_checkpoint_policy_outputs(*args, **kwargs):
                policy_dir.mkdir(parents=True, exist_ok=True)
                (policy_dir / "runs").mkdir(parents=True, exist_ok=True)
                for name in ("summary.json", "summary.csv", "leaderboard.md", "review_leaderboard.md"):
                    (policy_dir / name).write_text("checkpoint\n", encoding="utf-8")
                return {
                    "exclude_label_0_5": {
                        "directory": str(policy_dir),
                        "summary_json": str(policy_dir / "summary.json"),
                        "summary_csv": str(policy_dir / "summary.csv"),
                        "leaderboard_markdown": str(policy_dir / "leaderboard.md"),
                        "review_leaderboard_markdown": str(policy_dir / "review_leaderboard.md"),
                        "runs_dir": str(policy_dir / "runs"),
                        "html_report": "",
                        "eda_notebook": "",
                        "eda_notebook_executed": False,
                        "eda_notebook_execution_error": "",
                        "summary": {"runs": [{"benchmark_architecture": LOOP_CHUNK_BENCHMARK_ARCHITECTURE}]},
                    }
                }

            with patch(
                "bastirr.benchmarking.loop_runner._loop_experiment_root_for_mode",
                return_value=experiment_dir,
            ), patch(
                "bastirr.benchmarking.loop_runner.resolve_review_selection",
                return_value=[review_case],
            ), patch(
                "bastirr.benchmarking.loop_runner.resolve_model_presets",
                return_value=[gatekeeper_model],
            ), patch(
                "bastirr.benchmarking.loop_runner.get_model_preset",
                return_value=_ResolvedPresetWrapper(gatekeeper_model),
            ), patch(
                "bastirr.benchmarking.loop_runner.run_screening_chunk_loop_review",
                side_effect=_fake_chunk_runner,
            ), patch(
                "bastirr.benchmarking.loop_runner._checkpoint_policy_outputs",
                side_effect=_fake_checkpoint_policy_outputs,
            ), patch(
                "bastirr.benchmarking.loop_runner.write_policy_eda_notebook",
                return_value={
                    "notebook_path": str(policy_dir / "screening_results_analysis.ipynb"),
                    "executed": False,
                    "execution_error": "",
                },
            ), patch(
                "bastirr.benchmarking.loop_runner.write_policy_html_report",
                return_value={
                    "report_path": str(policy_dir / "screening_results_summary.html"),
                    "title": "Title",
                },
            ):
                _actual_dir, summary = run_screening_loop_benchmark(
                    suite_name="screening_ladder",
                    model_presets=["openai_gpt5"],
                    repeats=1,
                    orchestrator_policy="fixed",
                    orchestrator_model_key="openai_gpt5",
                    review_keys=[review_case.key],
                    gold_label_policies=["exclude_label_0_5"],
                    loop_mode="chunked",
                    chunk_count=2,
                    orchestrator_max_steps=30,
                )

            self.assertEqual(summary["benchmark_architecture"], LOOP_CHUNK_BENCHMARK_ARCHITECTURE)
            self.assertEqual(summary["loop_mode"], "chunked")
            self.assertEqual(chunk_runner_kwargs["chunk_count"], 2)
            self.assertIsNone(chunk_runner_kwargs["chunk_size"])
            self.assertEqual(chunk_runner_kwargs["orchestrator_max_steps"], 30)

    def test_rerun_screening_loop_reviews_in_experiment_replaces_selected_review(self):
        review_cases = [
            ScreeningBenchmarkReview(
                key="review_a",
                split="val",
                review_url="https://example.test/review-a",
                title="Review A",
                expected_n_studies=1,
                expected_n_screen_pass=1,
                expected_n_screen_exclude=0,
            ),
            ScreeningBenchmarkReview(
                key="review_b",
                split="val",
                review_url="https://example.test/review-b",
                title="Review B",
                expected_n_studies=2,
                expected_n_screen_pass=1,
                expected_n_screen_exclude=1,
            ),
        ]
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
            raw_runs_dir = experiment_dir / "_raw_runs"
            old_a_raw = raw_runs_dir / "old_a"
            old_b_raw = raw_runs_dir / "old_b"
            old_a_raw.mkdir(parents=True, exist_ok=True)
            old_b_raw.mkdir(parents=True, exist_ok=True)
            (old_a_raw / "evidence.json").write_text(json.dumps({
                "screening_decisions": [{"study_index": 1, "decision": "INCLUDE", "reason": "old a"}]
            }), encoding="utf-8")
            (old_b_raw / "evidence.json").write_text(json.dumps({
                "screening_decisions": [{"study_index": 1, "decision": "EXCLUDE", "reason": "old b"}]
            }), encoding="utf-8")

            include_policy_dir = experiment_dir / "include_policy"
            include_policy_dir.mkdir(parents=True, exist_ok=True)
            (experiment_dir / "benchmark_checkpoint.json").write_text(json.dumps({
                "suite": "screening_ladder",
                "benchmark_architecture": LOOP_BENCHMARK_ARCHITECTURE,
                "repeats": 1,
                "review_keys": ["review_a", "review_b"],
                "model_presets": ["openai_gpt5"],
                "orchestrator_policy": "fixed",
                "orchestrator_preset": "openai_gpt5",
                "gold_label_policies": ["include_label_0_5"],
                "completed_runs": [
                    {
                        "benchmark_run_id": "review_a_openai_gpt5_fixed_openai_gpt5_run1",
                        "review_key": "review_a",
                        "gatekeeper_preset": "openai_gpt5",
                        "orchestrator_policy": "fixed",
                        "orchestrator_preset": "openai_gpt5",
                        "run_index": 1,
                        "run_status": "completed",
                        "raw_run_dir": str(old_a_raw),
                    },
                    {
                        "benchmark_run_id": "review_b_openai_gpt5_fixed_openai_gpt5_run1",
                        "review_key": "review_b",
                        "gatekeeper_preset": "openai_gpt5",
                        "orchestrator_policy": "fixed",
                        "orchestrator_preset": "openai_gpt5",
                        "run_index": 1,
                        "run_status": "incomplete",
                        "raw_run_dir": str(old_b_raw),
                    },
                ],
            }), encoding="utf-8")
            (include_policy_dir / "summary.json").write_text(json.dumps({
                "runs": [
                    {
                        "benchmark_run_id": "review_a_openai_gpt5_fixed_openai_gpt5_run1",
                        "review_key": "review_a",
                        "gatekeeper_preset": "openai_gpt5",
                        "orchestrator_preset": "openai_gpt5",
                        "orchestrator_policy": "fixed",
                        "run_index": 1,
                        "duration_seconds": 1.0,
                        "run_status": "completed",
                        "error": "",
                        "screening_attempt_count": 1,
                        "rerun_triggered": False,
                        "benchmark_architecture": LOOP_BENCHMARK_ARCHITECTURE,
                    },
                    {
                        "benchmark_run_id": "review_b_openai_gpt5_fixed_openai_gpt5_run1",
                        "review_key": "review_b",
                        "gatekeeper_preset": "openai_gpt5",
                        "orchestrator_preset": "openai_gpt5",
                        "orchestrator_policy": "fixed",
                        "run_index": 1,
                        "duration_seconds": 2.0,
                        "run_status": "incomplete",
                        "error": "old failure",
                        "screening_attempt_count": 2,
                        "rerun_triggered": True,
                        "benchmark_architecture": LOOP_BENCHMARK_ARCHITECTURE,
                    },
                ]
            }), encoding="utf-8")
            materialized_raw_runs: list[list[dict]] = []

            def _fake_resolve_review_selection(_suite_name, review_keys=None):
                review_by_key = {review.key: review for review in review_cases}
                keys = review_keys or [review.key for review in review_cases]
                return [review_by_key[key] for key in keys]

            def _fake_run_screening_loop_review(**kwargs):
                review_case = kwargs["review_case"]
                self.assertEqual(review_case.key, "review_b")
                self.assertEqual(kwargs["orchestrator_max_steps"], 30)
                return {
                    "suite_name": "screening_ladder",
                    "review_case": review_case,
                    "review": SimpleNamespace(
                        title=review_case.title,
                        review_url=review_case.review_url,
                        studies=[object()] * review_case.expected_n_studies,
                    ),
                    "screening_decisions": [
                        {"study_index": 1, "decision": "INCLUDE", "reason": "new b"},
                        {"study_index": 2, "decision": "EXCLUDE", "reason": "new b"},
                    ],
                    "gatekeeper_model": model,
                    "orchestrator_model": model,
                    "orchestrator_policy": "fixed",
                    "run_index": 1,
                    "duration_seconds": 3.0,
                    "raw_run_dir": kwargs["output_root"] / "new_b",
                    "run_status": "completed",
                    "error": "",
                    "screening_attempt_count": 1,
                    "rerun_triggered": False,
                    "benchmark_architecture": LOOP_BENCHMARK_ARCHITECTURE,
                    "telemetry": {},
                }

            def _fake_checkpoint_policy_outputs(*args, **kwargs):
                materialized_raw_runs.append(kwargs["raw_runs"])
                return {
                    "include_label_0_5": {
                        "directory": str(include_policy_dir),
                        "summary_json": str(include_policy_dir / "summary.json"),
                        "summary_csv": str(include_policy_dir / "summary.csv"),
                        "leaderboard_markdown": str(include_policy_dir / "leaderboard.md"),
                        "review_leaderboard_markdown": str(include_policy_dir / "review_leaderboard.md"),
                        "runs_dir": str(include_policy_dir / "runs"),
                        "html_report": "",
                        "eda_notebook": "",
                        "eda_notebook_executed": False,
                        "eda_notebook_execution_error": "",
                        "summary": {"runs": []},
                    }
                }

            with patch(
                "bastirr.benchmarking.loop_runner.resolve_review_selection",
                side_effect=_fake_resolve_review_selection,
            ), patch(
                "bastirr.benchmarking.loop_runner.load_review",
                side_effect=lambda review_url, _split: SimpleNamespace(
                    title=review_url,
                    review_url=review_url,
                    studies=[object()],
                ),
            ), patch(
                "bastirr.benchmarking.loop_runner.get_model_preset",
                return_value=_ResolvedPresetWrapper(model),
            ), patch(
                "bastirr.benchmarking.loop_runner.run_screening_loop_review",
                side_effect=_fake_run_screening_loop_review,
            ), patch(
                "bastirr.benchmarking.loop_runner._checkpoint_policy_outputs",
                side_effect=_fake_checkpoint_policy_outputs,
            ), patch(
                "bastirr.benchmarking.loop_runner.write_policy_eda_notebook",
                return_value={
                    "notebook_path": str(include_policy_dir / "screening_results_analysis.ipynb"),
                    "executed": False,
                    "execution_error": "",
                },
            ), patch(
                "bastirr.benchmarking.loop_runner.write_policy_html_report",
                return_value={
                    "report_path": str(include_policy_dir / "screening_results_summary.html"),
                    "title": "Title",
                },
            ):
                _actual_dir, summary = rerun_screening_loop_reviews_in_experiment(
                    experiment_dir=experiment_dir,
                    review_keys=["review_b"],
                    execute_policy_notebooks=False,
                    orchestrator_max_steps=30,
                )

            self.assertEqual(summary["rerun_review_keys"], ["review_b"])
            self.assertEqual(summary["completed_raw_run_count"], 2)
            self.assertEqual(summary["orchestrator_max_steps"], 30)
            latest_raw_runs = materialized_raw_runs[-1]
            raw_by_review = {raw_run["review_case"].key: raw_run for raw_run in latest_raw_runs}
            self.assertEqual(raw_by_review["review_a"]["raw_run_dir"], old_a_raw)
            self.assertEqual(raw_by_review["review_b"]["run_status"], "completed")
            self.assertEqual(raw_by_review["review_b"]["raw_run_dir"], raw_runs_dir / "new_b")
            checkpoint = json.loads(
                (experiment_dir / "benchmark_checkpoint.json").read_text(encoding="utf-8")
            )
            replacement = [
                run
                for run in checkpoint["completed_runs"]
                if run["review_key"] == "review_b"
            ][0]
            self.assertEqual(replacement["run_status"], "completed")
            self.assertEqual(replacement["raw_run_dir"], str(raw_runs_dir / "new_b"))

    def test_totals_separate_architectures_and_size_bands(self):
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as tmpdir:
            output_root = Path(tmpdir) / "screening_benchmarks"
            for exp_name, architecture, review_key, n_studies, model, f1 in (
                ("exp_batch", "batch_orchestrator_v1", "review_100", 100, "deepseek_v4_pro", 0.8),
                ("exp_loop", "loop_orchestrator_v1", "review_101", 101, "deepseek_v4_pro", 0.9),
            ):
                policy_dir = output_root / exp_name / "exclude_policy"
                policy_dir.mkdir(parents=True, exist_ok=True)
                (policy_dir / "summary.json").write_text(json.dumps({
                    "suite": "screening_ladder",
                    "repeats": 1,
                    "gold_label_policy": "exclude_label_0_5",
                    "runs": [{
                        "suite": "screening_ladder",
                        "gold_label_policy": "exclude_label_0_5",
                        "benchmark_architecture": architecture,
                        "review_key": review_key,
                        "review_title": review_key,
                        "review_url": "https://example.test",
                        "split": "dev",
                        "n_studies": n_studies,
                        "gold_pass_count": 1,
                        "gold_exclude_count": 1,
                        "gatekeeper_preset": model,
                        "gatekeeper_model_label": "legacy-provider-label",
                        "gatekeeper_backend": "openai",
                        "gatekeeper_api_base": "https://api.deepseek.com",
                        "orchestrator_policy": "fixed",
                        "orchestrator_preset": "openai_gpt5",
                        "orchestrator_model_label": "gpt-5",
                        "orchestrator_backend": "openai",
                        "orchestrator_api_base": "",
                        "run_status": "completed",
                        "scored_for_aggregate": True,
                        "parse_success": True,
                        "decision_coverage": 1.0,
                        "accuracy": f1,
                        "precision": f1,
                        "recall": f1,
                        "specificity": f1,
                        "f1": f1,
                        "duration_seconds": 10.0,
                        "total_tokens": 100,
                        "total_steps": 5,
                    }],
                }), encoding="utf-8")
            include_policy_dir = output_root / "exp_batch" / "include_policy"
            include_policy_dir.mkdir(parents=True, exist_ok=True)
            (include_policy_dir / "summary.json").write_text(json.dumps({
                "suite": "screening_ladder",
                "repeats": 1,
                "gold_label_policy": "include_label_0_5",
                "runs": [{
                    "suite": "screening_ladder",
                    "gold_label_policy": "include_label_0_5",
                    "benchmark_architecture": "batch_orchestrator_v1",
                    "review_key": "review_100",
                    "review_title": "review_100",
                    "review_url": "https://example.test",
                    "split": "dev",
                    "n_studies": 100,
                    "gold_pass_count": 1,
                    "gold_exclude_count": 1,
                    "gatekeeper_preset": "deepseek_v4_pro",
                    "gatekeeper_model_label": "deepseek-v4-pro [DeepSeek V4 Pro]",
                    "gatekeeper_backend": "openai",
                    "gatekeeper_api_base": "https://api.deepseek.com",
                    "orchestrator_policy": "fixed",
                    "orchestrator_preset": "openai_gpt5",
                    "orchestrator_model_label": "gpt-5",
                    "orchestrator_backend": "openai",
                    "orchestrator_api_base": "",
                    "run_status": "completed",
                    "scored_for_aggregate": True,
                    "parse_success": True,
                    "decision_coverage": 1.0,
                    "accuracy": 0.2,
                    "precision": 0.2,
                    "recall": 0.2,
                    "specificity": 0.2,
                    "f1": 0.2,
                    "duration_seconds": 10.0,
                    "total_tokens": 100,
                    "total_steps": 5,
                }],
            }), encoding="utf-8")
            duplicate_policy_dir = output_root / "exp_batch_repeated_calibration" / "exclude_policy"
            duplicate_policy_dir.mkdir(parents=True, exist_ok=True)
            (duplicate_policy_dir / "summary.json").write_text(json.dumps({
                "suite": "screening_ladder",
                "repeats": 5,
                "gold_label_policy": "exclude_label_0_5",
                "runs": [{
                    "suite": "screening_ladder",
                    "gold_label_policy": "exclude_label_0_5",
                    "benchmark_architecture": "batch_orchestrator_v1",
                    "review_key": "review_100",
                    "review_title": "review_100",
                    "review_url": "https://example.test",
                    "split": "dev",
                    "n_studies": 100,
                    "gold_pass_count": 1,
                    "gold_exclude_count": 1,
                    "gatekeeper_preset": "deepseek_v4_pro",
                    "gatekeeper_model_label": "deepseek-v4-pro [DeepSeek V4 Pro]",
                    "gatekeeper_backend": "openai",
                    "gatekeeper_api_base": "https://openrouter.ai/api/v1",
                    "orchestrator_policy": "fixed",
                    "orchestrator_preset": "openai_gpt5",
                    "orchestrator_model_label": "gpt-5",
                    "orchestrator_backend": "openai",
                    "orchestrator_api_base": "",
                    "run_status": "completed",
                    "scored_for_aggregate": True,
                    "parse_success": True,
                    "decision_coverage": 1.0,
                    "accuracy": 0.1,
                    "precision": 0.1,
                    "recall": 0.1,
                    "specificity": 0.1,
                    "f1": 0.1,
                    "duration_seconds": 10.0,
                    "total_tokens": 100,
                    "total_steps": 5,
                }],
            }), encoding="utf-8")
            cross_suite_duplicate_policy_dir = (
                output_root / "20260601_000000_other_suite_run" / "exclude_policy"
            )
            cross_suite_duplicate_policy_dir.mkdir(parents=True, exist_ok=True)
            (cross_suite_duplicate_policy_dir / "summary.json").write_text(json.dumps({
                "suite": "other_screening_ladder",
                "repeats": 1,
                "gold_label_policy": "exclude_label_0_5",
                "runs": [{
                    "suite": "other_screening_ladder",
                    "gold_label_policy": "exclude_label_0_5",
                    "benchmark_architecture": "batch_orchestrator_v1",
                    "review_key": "review_100",
                    "review_title": "review_100",
                    "review_url": "https://example.test",
                    "split": "dev",
                    "n_studies": 100,
                    "gold_pass_count": 1,
                    "gold_exclude_count": 1,
                    "gatekeeper_preset": "deepseek_v4_pro",
                    "gatekeeper_model_label": "deepseek-v4-pro [DeepSeek V4 Pro]",
                    "gatekeeper_backend": "openai",
                    "gatekeeper_api_base": "https://openrouter.ai/api/v1",
                    "orchestrator_policy": "fixed",
                    "orchestrator_preset": "openai_gpt5",
                    "orchestrator_model_label": "gpt-5",
                    "orchestrator_backend": "openai",
                    "orchestrator_api_base": "",
                    "run_status": "completed",
                    "scored_for_aggregate": True,
                    "parse_success": True,
                    "decision_coverage": 1.0,
                    "accuracy": 0.6,
                    "precision": 0.6,
                    "recall": 0.6,
                    "specificity": 0.6,
                    "f1": 0.6,
                    "duration_seconds": 10.0,
                    "total_tokens": 100,
                    "total_steps": 5,
                }],
            }), encoding="utf-8")
            repetition_policy_dir = (
                output_root / "20260701_000000_screening_ladder_rep2" / "exclude_policy"
            )
            repetition_policy_dir.mkdir(parents=True, exist_ok=True)
            (repetition_policy_dir / "summary.json").write_text(json.dumps({
                "suite": "screening_ladder",
                "repeats": 1,
                "gold_label_policy": "exclude_label_0_5",
                "runs": [{
                    "suite": "screening_ladder",
                    "gold_label_policy": "exclude_label_0_5",
                    "benchmark_architecture": "batch_orchestrator_v1",
                    "review_key": "review_100",
                    "review_title": "review_100",
                    "review_url": "https://example.test",
                    "split": "dev",
                    "n_studies": 100,
                    "gold_pass_count": 1,
                    "gold_exclude_count": 1,
                    "gatekeeper_preset": "deepseek_v4_pro",
                    "gatekeeper_model_label": "deepseek-v4-pro [DeepSeek V4 Pro]",
                    "gatekeeper_backend": "openai",
                    "gatekeeper_api_base": "https://openrouter.ai/api/v1",
                    "orchestrator_policy": "fixed",
                    "orchestrator_preset": "openai_gpt5",
                    "orchestrator_model_label": "gpt-5",
                    "orchestrator_backend": "openai",
                    "orchestrator_api_base": "",
                    "run_status": "completed",
                    "scored_for_aggregate": True,
                    "parse_success": True,
                    "decision_coverage": 1.0,
                    "accuracy": 0.99,
                    "precision": 0.99,
                    "recall": 0.99,
                    "specificity": 0.99,
                    "f1": 0.99,
                    "duration_seconds": 10.0,
                    "total_tokens": 100,
                    "total_steps": 5,
                }],
            }), encoding="utf-8")
            incomplete_policy_dir = (
                output_root / "20260801_000000_screening_ladder_partial" / "exclude_policy"
            )
            incomplete_policy_dir.mkdir(parents=True, exist_ok=True)
            partial_rows = []
            for review_key, scored, f1 in (
                ("partial_review_10", True, 0.99),
                ("partial_review_25", False, 0.0),
            ):
                partial_rows.append({
                    "suite": "screening_ladder",
                    "gold_label_policy": "exclude_label_0_5",
                    "benchmark_architecture": "batch_orchestrator_v1",
                    "review_key": review_key,
                    "review_title": review_key,
                    "review_url": "https://example.test",
                    "split": "dev",
                    "n_studies": 10 if review_key.endswith("_10") else 25,
                    "gold_pass_count": 1,
                    "gold_exclude_count": 1,
                    "gatekeeper_preset": "partial_model",
                    "gatekeeper_model_label": "partial-model",
                    "gatekeeper_backend": "openai",
                    "gatekeeper_api_base": "",
                    "orchestrator_policy": "fixed",
                    "orchestrator_preset": "openai_gpt5",
                    "orchestrator_model_label": "gpt-5",
                    "orchestrator_backend": "openai",
                    "orchestrator_api_base": "",
                    "run_index": 1,
                    "run_status": "completed" if scored else "incomplete",
                    "scored_for_aggregate": scored,
                    "parse_success": scored,
                    "decision_coverage": 1.0 if scored else 0.0,
                    "screening_decision_count": 10 if scored else 0,
                    "missing_decision_count": 0 if scored else (10 if review_key.endswith("_10") else 25),
                    "incomplete_reason": "" if scored else "missing 25 decisions",
                    "accuracy": f1,
                    "precision": f1,
                    "recall": f1,
                    "specificity": f1,
                    "f1": f1,
                    "duration_seconds": 10.0,
                    "total_tokens": 100,
                    "total_steps": 5,
                })
            (incomplete_policy_dir / "summary.json").write_text(json.dumps({
                "suite": "screening_ladder",
                "repeats": 1,
                "review_keys": ["partial_review_10", "partial_review_25"],
                "gold_label_policy": "exclude_label_0_5",
                "runs": partial_rows,
            }), encoding="utf-8")

            stale_suite_horizontal = (
                output_root
                / "totals"
                / "screening_ladder"
                / "exclude_policy"
                / "loop_orchestrator_v1"
                / "horizontal_size_bands.json"
            )
            stale_suite_horizontal.parent.mkdir(parents=True, exist_ok=True)
            stale_suite_horizontal.write_text("{}", encoding="utf-8")

            result = write_screening_totals(
                output_root=output_root,
                write_incomplete_report=True,
            )

            self.assertEqual(size_band_for(100)["key"], "upper_mid_100")
            self.assertEqual(size_band_for(101)["key"], "large_100_plus")
            group_dirs = {Path(group["directory"]).name for group in result["groups"]}
            self.assertIn("batch_orchestrator_v1", group_dirs)
            self.assertIn("loop_orchestrator_v1", group_dirs)
            self.assertFalse(stale_suite_horizontal.exists())

            loop_size_bands = json.loads((
                output_root
                / "totals"
                / "horizontal_comparison"
                / "exclude_policy"
                / "loop_orchestrator_v1"
                / "horizontal_size_bands.json"
            ).read_text(encoding="utf-8"))
            self.assertEqual(loop_size_bands["size_bands"][0]["size_band"], "large_100_plus")
            self.assertEqual(
                loop_size_bands["size_bands"][0]["review_rows"][0]["review_key"],
                "review_101",
            )
            self.assertEqual(
                loop_size_bands["size_bands"][0]["review_rows"][0]["suite"],
                "screening_ladder",
            )
            batch_size_bands = json.loads((
                output_root
                / "totals"
                / "horizontal_comparison"
                / "exclude_policy"
                / "batch_orchestrator_v1"
                / "horizontal_size_bands.json"
            ).read_text(encoding="utf-8"))
            batch_review_rows = batch_size_bands["size_bands"][0]["review_rows"]
            self.assertEqual(len(batch_review_rows), 1)
            self.assertEqual(batch_review_rows[0]["review_key"], "review_100")
            self.assertEqual(batch_review_rows[0]["suite"], "other_screening_ladder")
            self.assertEqual(batch_review_rows[0]["n_runs"], 1)
            self.assertEqual(batch_review_rows[0]["mean_f1"], 0.6)
            totals_index = json.loads((
                output_root
                / "totals"
                / "totals_index.json"
            ).read_text(encoding="utf-8"))
            self.assertTrue(result["incomplete_runs_report"].endswith("incomplete_runs_report.json"))
            self.assertTrue(totals_index["incomplete_runs_report"].endswith("incomplete_runs_report.json"))
            incomplete_report = json.loads((
                output_root
                / "totals"
                / "incomplete_runs_report.json"
            ).read_text(encoding="utf-8"))
            self.assertEqual(incomplete_report["n_incomplete_or_unscored_runs"], 1)
            self.assertEqual(incomplete_report["n_excluded_incomplete_model_groups"], 1)
            incomplete_group = incomplete_report["groups"][0]
            self.assertEqual(
                incomplete_group["excluded_incomplete_model_groups"][0]["missing_review_keys"],
                ["partial_review_25"],
            )
            self.assertEqual(
                incomplete_group["incomplete_or_unscored_runs"][0]["review_key"],
                "partial_review_25",
            )
            self.assertEqual(
                incomplete_group["incomplete_or_unscored_runs"][0]["missing_decision_count"],
                25,
            )
            self.assertTrue((
                output_root
                / "totals"
                / "incomplete_runs_report.md"
            ).exists())
            self.assertFalse(totals_index["totals_root"].startswith("/"))
            self.assertTrue(all(
                not group["directory"].startswith("/")
                for group in totals_index["groups"]
            ))
            self.assertTrue(totals_index["horizontal_comparison_groups"])
            batch_leaderboard = json.loads((
                output_root
                / "totals"
                / "screening_ladder"
                / "exclude_policy"
                / "batch_orchestrator_v1"
                / "totals_leaderboard.json"
            ).read_text(encoding="utf-8"))
            self.assertEqual(batch_leaderboard["leaderboard"][0]["n_runs"], 1)
            self.assertEqual(batch_leaderboard["leaderboard"][0]["mean_f1"], 0.8)
            self.assertEqual(
                batch_leaderboard["leaderboard"][0]["gatekeeper_model_label"],
                "deepseek-v4-pro [DeepSeek V4 Pro]",
            )
            self.assertFalse(any(
                row["gatekeeper_preset"] == "partial_model"
                for row in batch_leaderboard["leaderboard"]
            ))
            self.assertEqual(
                batch_leaderboard["excluded_incomplete_model_groups"][0]["gatekeeper_preset"],
                "partial_model",
            )
            self.assertEqual(
                batch_leaderboard["excluded_incomplete_model_groups"][0]["n_scored_runs"],
                1,
            )
            self.assertEqual(
                batch_leaderboard["excluded_incomplete_model_groups"][0]["n_expected_runs"],
                2,
            )
            canonical_manifest = write_canonical_sources(output_root=output_root)
            self.assertTrue(canonical_manifest["canonical_sources_path"].endswith("canonical_sources.json"))
            self.assertEqual(canonical_manifest["n_sources"], 4)
            self.assertEqual(canonical_manifest["n_excluded_repetition_folder_runs"], 1)
            self.assertTrue(all(
                source["source_repeats"] == 1
                for source in canonical_manifest["sources"]
            ))
            self.assertEqual(
                {source["gold_label_policy"] for source in canonical_manifest["sources"]},
                {"exclude_label_0_5"},
            )
            self.assertFalse(any(
                "_rep2" in source["source_experiment_dir"]
                for source in canonical_manifest["sources"]
            ))
            self.assertNotIn("canonical_sources_audit_md_path", canonical_manifest)
            self.assertNotIn("canonical_sources_audit_json_path", canonical_manifest)
            self.assertFalse((
                output_root
                / "totals"
                / "canonical_sources_audit.md"
            ).exists())
            self.assertFalse((
                output_root
                / "totals"
                / "canonical_sources_audit.json"
            ).exists())
            canonical_result = write_screening_totals(
                output_root=output_root,
                source_mode="canonical",
            )
            self.assertEqual(canonical_result["source_mode"], "canonical")
            canonical_batch_leaderboard = json.loads((
                output_root
                / "totals"
                / "screening_ladder"
                / "exclude_policy"
                / "batch_orchestrator_v1"
                / "totals_leaderboard.json"
            ).read_text(encoding="utf-8"))
            self.assertEqual(canonical_batch_leaderboard["source_mode"], "canonical")
            self.assertEqual(canonical_batch_leaderboard["leaderboard"][0]["n_runs"], 1)
            self.assertEqual(canonical_batch_leaderboard["leaderboard"][0]["mean_f1"], 0.8)
            self.assertFalse(any(
                row["gatekeeper_preset"] == "partial_model"
                for row in canonical_batch_leaderboard["leaderboard"]
            ))
            self.assertEqual(
                canonical_batch_leaderboard["excluded_incomplete_model_groups"][0]["gatekeeper_preset"],
                "partial_model",
            )

    def test_canonical_policy_filter_selects_policy_from_multi_policy_manifest(self):
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as tmpdir:
            output_root = Path(tmpdir) / "screening_benchmarks"
            for policy, policy_dir_name, f1 in (
                ("exclude_label_0_5", "exclude_policy", 0.8),
                ("include_label_0_5", "include_policy", 0.2),
            ):
                policy_dir = output_root / "exp" / policy_dir_name
                policy_dir.mkdir(parents=True, exist_ok=True)
                (policy_dir / "summary.json").write_text(json.dumps({
                    "suite": "screening_ladder",
                    "repeats": 1,
                    "review_keys": ["review_10"],
                    "gold_label_policy": policy,
                    "runs": [{
                        "suite": "screening_ladder",
                        "gold_label_policy": policy,
                        "benchmark_architecture": "batch_orchestrator_v1",
                        "review_key": "review_10",
                        "review_title": "Review 10",
                        "review_url": "https://example.test",
                        "split": "dev",
                        "n_studies": 10,
                        "gold_pass_count": 1,
                        "gold_exclude_count": 1,
                        "gatekeeper_preset": "deepseek_v4_pro",
                        "gatekeeper_model_label": "deepseek-v4-pro [DeepSeek V4 Pro]",
                        "gatekeeper_backend": "openai",
                        "gatekeeper_api_base": "",
                        "orchestrator_policy": "fixed",
                        "orchestrator_preset": "openai_gpt5",
                        "orchestrator_model_label": "gpt-5",
                        "orchestrator_backend": "openai",
                        "orchestrator_api_base": "",
                        "run_index": 1,
                        "run_status": "completed",
                        "scored_for_aggregate": True,
                        "parse_success": True,
                        "decision_coverage": 1.0,
                        "accuracy": f1,
                        "precision": f1,
                        "recall": f1,
                        "specificity": f1,
                        "f1": f1,
                    }],
                }), encoding="utf-8")

            manifest = write_canonical_sources(
                output_root=output_root,
                gold_label_policies=["exclude_label_0_5", "include_label_0_5"],
            )
            self.assertEqual(
                set(manifest["canonical_gold_label_policies"]),
                {"exclude_label_0_5", "include_label_0_5"},
            )

            exclude_result = write_screening_totals(
                output_root=output_root,
                source_mode="canonical",
                canonical_gold_label_policies=["exclude_label_0_5"],
            )
            self.assertEqual(len(exclude_result["groups"]), 1)
            self.assertEqual(exclude_result["groups"][0]["gold_label_policy"], "exclude_label_0_5")

            all_result = write_screening_totals(
                output_root=output_root,
                source_mode="canonical",
                canonical_gold_label_policies=[],
            )
            self.assertEqual(
                {group["gold_label_policy"] for group in all_result["groups"]},
                {"exclude_label_0_5", "include_label_0_5"},
            )

    def test_merge_canonical_sources_unions_manifests_and_dedupes(self):
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as tmpdir:
            output_root = Path(tmpdir) / "screening_benchmarks"
            totals_root = output_root / "totals"
            remote_root = output_root / "totals_remote"
            summary_a = output_root / "exp_a" / "exclude_policy" / "summary.json"
            summary_b = output_root / "exp_b" / "exclude_policy" / "summary.json"
            summary_rep = output_root / "exp_rep2" / "exclude_policy" / "summary.json"
            summary_a.parent.mkdir(parents=True, exist_ok=True)
            summary_b.parent.mkdir(parents=True, exist_ok=True)
            summary_rep.parent.mkdir(parents=True, exist_ok=True)

            def _run(review_key: str, model: str) -> dict:
                return {
                    "suite": "screening_ladder",
                    "gold_label_policy": "exclude_label_0_5",
                    "benchmark_architecture": "batch_orchestrator_v1",
                    "review_key": review_key,
                    "review_title": review_key,
                    "n_studies": 10,
                    "gatekeeper_preset": model,
                    "gatekeeper_model_label": model,
                    "orchestrator_policy": "fixed",
                    "orchestrator_preset": model,
                    "orchestrator_model_label": model,
                    "run_index": 1,
                    "run_status": "completed",
                    "scored_for_aggregate": True,
                }

            summary_a.write_text(json.dumps({
                "suite": "screening_ladder",
                "gold_label_policy": "exclude_label_0_5",
                "repeats": 1,
                "runs": [_run("review_a", "model_a")],
            }), encoding="utf-8")
            summary_b.write_text(json.dumps({
                "suite": "screening_ladder",
                "gold_label_policy": "exclude_label_0_5",
                "repeats": 1,
                "runs": [
                    _run("review_a", "model_a"),
                    _run("review_b", "model_b"),
                ],
            }), encoding="utf-8")
            summary_rep.write_text(json.dumps({
                "suite": "screening_ladder",
                "gold_label_policy": "exclude_label_0_5",
                "repeats": 1,
                "runs": [_run("review_c", "model_c")],
            }), encoding="utf-8")

            def _source(review_key: str, model: str, summary_path: Path, stamp: str) -> dict:
                return {
                    "suite": "screening_ladder",
                    "gold_label_policy": "exclude_label_0_5",
                    "benchmark_architecture": "batch_orchestrator_v1",
                    "review_key": review_key,
                    "review_title": review_key,
                    "n_studies": 10,
                    "gatekeeper_preset": model,
                    "gatekeeper_model_label": model,
                    "orchestrator_policy": "fixed",
                    "orchestrator_preset": model,
                    "orchestrator_model_label": model,
                    "run_index": 1,
                    "run_status": "completed",
                    "scored_for_aggregate": True,
                    "source_repeats": 1,
                    "source_timestamp": stamp,
                    "source_summary_json": str(summary_path),
                    "source_experiment_dir": str(summary_path.parent.parent),
                    "selection_reason": "test",
                }

            totals_root.mkdir(parents=True, exist_ok=True)
            remote_root.mkdir(parents=True, exist_ok=True)
            (totals_root / "canonical_sources.json").write_text(json.dumps({
                "version": 1,
                "canonical_gold_label_policies": ["exclude_label_0_5"],
                "n_discovered_runs": 10,
                "n_completed_scored_repeat_eligible_runs": 3,
                "n_excluded_repetition_folder_runs": 1,
                "n_eligible_runs": 2,
                "sources": [
                    _source("review_a", "model_a", summary_a, "2026-01-01|20260101_000000"),
                ],
            }), encoding="utf-8")
            (remote_root / "canonical_sources.json").write_text(json.dumps({
                "version": 1,
                "canonical_gold_label_policies": ["exclude_label_0_5"],
                "sources": [
                    _source("review_a", "model_a", summary_b, "2026-01-02|20260102_000000"),
                    _source("review_b", "model_b", summary_b, "2026-01-02|20260102_000000"),
                ],
            }), encoding="utf-8")

            merged = merge_canonical_sources(
                totals_root=totals_root,
                source_manifest_paths=[remote_root / "canonical_sources.json"],
            )

            self.assertEqual(merged["n_input_sources"], 3)
            self.assertEqual(merged["n_deduplicated_sources"], 1)
            self.assertEqual(merged["n_sources"], 2)
            persisted = json.loads((totals_root / "canonical_sources.json").read_text())
            self.assertEqual(persisted["selection_mode"], "explicit_manifest")
            self.assertNotIn("merged_from", persisted)
            self.assertNotIn("n_input_sources", persisted)
            self.assertNotIn("n_deduplicated_sources", persisted)
            self.assertNotIn("source_manifest_counts", persisted)
            self.assertEqual(persisted["n_discovered_runs"], 4)
            self.assertEqual(persisted["n_completed_scored_repeat_eligible_runs"], 4)
            self.assertEqual(persisted["n_excluded_repetition_folder_runs"], 1)
            self.assertEqual(persisted["n_eligible_runs"], 3)
            self.assertTrue(all(
                source.get("selection_reason") != "merged from canonical source manifests"
                for source in persisted["sources"]
            ))
            sources_by_review = {
                source["review_key"]: source
                for source in merged["sources"]
            }
            self.assertEqual(
                sources_by_review["review_a"]["source_summary_json"],
                str(summary_b.resolve().relative_to(Path.cwd())),
            )
            self.assertEqual(
                sources_by_review["review_b"]["source_summary_json"],
                str(summary_b.resolve().relative_to(Path.cwd())),
            )

    def test_register_canonical_sources_from_experiment_replaces_same_variant(self):
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as tmpdir:
            output_root = Path(tmpdir) / "screening_benchmarks"
            totals_root = output_root / "totals"
            old_policy_dir = output_root / "old_exp" / "exclude_policy"
            old_policy_dir.mkdir(parents=True, exist_ok=True)
            new_policy_dir = output_root / "new_exp" / "exclude_policy"
            new_policy_dir.mkdir(parents=True, exist_ok=True)

            def _summary(f1: float, repeats: int = 1) -> dict:
                return {
                    "suite": "screening_ladder",
                    "repeats": repeats,
                    "gold_label_policy": "exclude_label_0_5",
                    "runs": [{
                        "suite": "screening_ladder",
                        "gold_label_policy": "exclude_label_0_5",
                        "benchmark_architecture": "batch_orchestrator_v1",
                        "review_key": "review_10",
                        "review_title": "review_10",
                        "review_url": "https://example.test",
                        "split": "dev",
                        "n_studies": 10,
                        "gold_pass_count": 1,
                        "gold_exclude_count": 1,
                        "gatekeeper_preset": "deepseek_v4_pro",
                        "gatekeeper_model_label": "deepseek-v4-pro [DeepSeek V4 Pro]",
                        "orchestrator_policy": "fixed",
                        "orchestrator_preset": "openai_gpt5",
                        "orchestrator_model_label": "gpt-5",
                        "run_index": 1,
                        "run_status": "completed",
                        "scored_for_aggregate": True,
                        "parse_success": True,
                        "decision_coverage": 1.0,
                        "accuracy": f1,
                        "precision": f1,
                        "recall": f1,
                        "specificity": f1,
                        "f1": f1,
                    }],
                }

            (old_policy_dir / "summary.json").write_text(
                json.dumps(_summary(0.3)),
                encoding="utf-8",
            )
            (new_policy_dir / "summary.json").write_text(
                json.dumps(_summary(0.9)),
                encoding="utf-8",
            )

            register_canonical_sources_from_experiment(
                output_root / "old_exp",
                totals_root=totals_root,
                mode="auto",
            )
            stale_manifest_path = totals_root / "canonical_sources.json"
            stale_manifest = json.loads(stale_manifest_path.read_text(encoding="utf-8"))
            stale_manifest["n_sources"] = 999
            stale_manifest_path.write_text(json.dumps(stale_manifest), encoding="utf-8")
            register_canonical_sources_from_experiment(
                output_root / "new_exp",
                totals_root=totals_root,
                mode="auto",
            )
            persisted_manifest = json.loads(stale_manifest_path.read_text(encoding="utf-8"))
            self.assertEqual(
                persisted_manifest["n_sources"],
                len(persisted_manifest["sources"]),
            )
            result = write_screening_totals(
                output_root=output_root,
                totals_root=totals_root,
                source_mode="canonical",
            )
            self.assertEqual(result["source_mode"], "canonical")
            leaderboard = json.loads((
                totals_root
                / "screening_ladder"
                / "exclude_policy"
                / "batch_orchestrator_v1"
                / "totals_leaderboard.json"
            ).read_text(encoding="utf-8"))
            self.assertEqual(leaderboard["leaderboard"][0]["n_runs"], 1)
            self.assertEqual(leaderboard["leaderboard"][0]["mean_f1"], 0.9)
