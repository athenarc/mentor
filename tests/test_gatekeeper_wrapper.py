"""Unit tests for strict gatekeeper wrapper and context-overflow fail-fast."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from smolagents import ActionStep

from bastirr.agents.wrappers import (
    GATEKEEPER_BATCH_TASK,
    GATEKEEPER_CHUNK_TASK,
    GATEKEEPER_SINGLE_STUDY_TASK,
    PAYLOAD_KEY_CANDIDATES_JSON,
    PAYLOAD_KEY_CANDIDATE_STUDY,
    PAYLOAD_KEY_CHUNK_DATA,
    wrap_gatekeeper,
)
from bastirr.agents.wrappers.gatekeeper import _StrictGatekeeperWrapper
from bastirr.benchmarking.model_presets import ResolvedModelPreset
from bastirr.benchmarking.review_suites import ScreeningBenchmarkReview
from bastirr.data import Study, SystematicReview
from bastirr.errors import (
    ContextOverflowError,
    ErrorClassifier,
    abort_on_classified_error,
    is_context_overflow_error,
    make_error_abort_callback,
    with_error_abort_callback,
)


def _study_payload(**overrides):
    base = {
        "study_index": 1,
        "title": "Example title",
        "abstract": "Example abstract long enough to look like a study.",
    }
    base.update(overrides)
    return base


class ContextOverflowClassificationTests(unittest.TestCase):
    def test_detects_openrouter_style_message_with_400(self):
        self.assertTrue(
            is_context_overflow_error(
                "Error code: 400 - {'error': {'message': "
                "\"This endpoint's maximum context length is 163840 tokens.\", "
                "'code': 400}}"
            )
        )

    def test_detects_openai_semantic_code(self):
        self.assertTrue(
            is_context_overflow_error(
                "Error code: 400 - {'error': {'message': 'too long', "
                "'code': 'context_length_exceeded'}}"
            )
        )

    def test_requires_both_message_and_400(self):
        self.assertFalse(
            is_context_overflow_error(
                "This endpoint's maximum context length is 163840 tokens."
            )
        )
        self.assertFalse(
            is_context_overflow_error("Error code: 400 - {'error': {'message': 'bad json'}}")
        )

    def test_detects_context_overflow_error_instance(self):
        self.assertTrue(is_context_overflow_error(ContextOverflowError("too long")))

    def test_ignores_unrelated_errors(self):
        self.assertFalse(is_context_overflow_error(ValueError("missing key")))
        self.assertFalse(is_context_overflow_error("rate limit exceeded"))


class GatekeeperWrapperTests(unittest.TestCase):
    def test_forces_fixed_task_and_keeps_payload_in_additional_args(self):
        calls = []

        class FakeAgent:
            name = "gatekeeper"

            def __call__(self, task="", additional_args=None, **kwargs):
                calls.append({
                    "task": task,
                    "additional_args": additional_args,
                    "kwargs": kwargs,
                })
                return "ok"

        wrapped = wrap_gatekeeper(
            FakeAgent(),
            payload_key=PAYLOAD_KEY_CANDIDATES_JSON,
            fixed_task=GATEKEEPER_BATCH_TASK,
        )
        payload = {"studies": [_study_payload()]}
        result = wrapped(
            "LLM wrote a huge task with study JSON here",
            additional_args={PAYLOAD_KEY_CANDIDATES_JSON: payload},
        )

        self.assertEqual(result, "ok")
        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0]["task"], GATEKEEPER_BATCH_TASK)
        self.assertEqual(
            calls[0]["additional_args"][PAYLOAD_KEY_CANDIDATES_JSON],
            payload,
        )
        self.assertNotIn("study JSON", calls[0]["task"])

    def test_rejects_missing_additional_args(self):
        calls = []

        class FakeAgent:
            name = "gatekeeper"

            def __call__(self, *args, **kwargs):
                calls.append((args, kwargs))
                return "ok"

        wrapped = wrap_gatekeeper(
            FakeAgent(),
            payload_key=PAYLOAD_KEY_CANDIDATE_STUDY,
            fixed_task=GATEKEEPER_SINGLE_STUDY_TASK,
        )
        with self.assertRaises(ValueError):
            wrapped("task", additional_args=None)
        self.assertEqual(calls, [])

    def test_rejects_indices_only_payload(self):
        calls = []

        class FakeAgent:
            name = "gatekeeper"

            def __call__(self, *args, **kwargs):
                calls.append((args, kwargs))
                return "ok"

        wrapped = wrap_gatekeeper(
            FakeAgent(),
            payload_key=PAYLOAD_KEY_CHUNK_DATA,
            fixed_task=GATEKEEPER_CHUNK_TASK,
        )
        with self.assertRaises(ValueError):
            wrapped(
                "screen",
                additional_args={
                    PAYLOAD_KEY_CHUNK_DATA: {"chunk_study_indices": [1, 2, 3]},
                },
            )
        self.assertEqual(calls, [])

    def test_overflow_exception_becomes_context_overflow_error(self):
        class OverflowAgent:
            name = "gatekeeper"

            def __call__(self, task="", additional_args=None, **kwargs):
                raise RuntimeError(
                    "Error code: 400 - {'error': {'message': "
                    "\"This endpoint's maximum context length is 163840 tokens. "
                    "However, you requested about 200000 tokens.\", 'code': 400}}"
                )

        wrapped = wrap_gatekeeper(
            OverflowAgent(),
            payload_key=PAYLOAD_KEY_CANDIDATES_JSON,
            fixed_task=GATEKEEPER_BATCH_TASK,
        )
        with self.assertRaises(ContextOverflowError):
            wrapped(
                "ignored",
                additional_args={
                    PAYLOAD_KEY_CANDIDATES_JSON: {"studies": [_study_payload()]},
                },
            )


class OverflowAbortCallbackTests(unittest.TestCase):
    def test_abort_callback_raises_on_overflow_step_error(self):
        step = ActionStep(step_number=2, timing=SimpleNamespace(start=0, end=0))
        step.error = (
            "Error code: 400 - {'error': {'message': "
            "\"This endpoint's maximum context length is 262144 tokens.\", 'code': 400}}"
        )
        with self.assertRaises(ContextOverflowError):
            abort_on_classified_error(step, agent=SimpleNamespace(name="orchestrator"))

    def test_with_error_abort_callback_preserves_dict_shape(self):
        def existing(step, agent=None, **kwargs):
            return None

        callbacks = {ActionStep: [existing]}
        updated = with_error_abort_callback(callbacks)
        self.assertIsInstance(updated, dict)
        self.assertIn(existing, updated[ActionStep])
        self.assertIn(abort_on_classified_error, updated[ActionStep])

    def test_custom_classifier_can_abort_on_other_errors(self):
        class QuotaExceededError(RuntimeError):
            pass

        classifier = ErrorClassifier(
            name="quota_exceeded",
            exception_type=QuotaExceededError,
            matches=lambda err: "insufficient_quota" in str(err),
        )
        abort = make_error_abort_callback((classifier,))
        step = ActionStep(step_number=1, timing=SimpleNamespace(start=0, end=0))
        step.error = "Error code: 429 - insufficient_quota"
        with self.assertRaises(QuotaExceededError):
            abort(step, agent=SimpleNamespace(name="orchestrator"))


class _FakeNamedGatekeeper:
    name = "gatekeeper"
    description = "Screens candidate studies."

    def __call__(self, *args, **kwargs):
        return "ok"


class OrchestratorManagedAgentTests(unittest.TestCase):
    def test_batch_orchestrator_exposes_named_gatekeeper(self):
        with patch(
            "bastirr.agents.screening_orchestrator.create_gatekeeper_agent",
            return_value=_FakeNamedGatekeeper(),
        ), patch("bastirr.agents.screening_orchestrator.CodeAgent") as code_agent:
            from bastirr.agents.screening_orchestrator import (
                create_screening_orchestrator_agent,
            )

            create_screening_orchestrator_agent(MagicMock(), MagicMock())
            kwargs = code_agent.call_args.kwargs
            self.assertEqual(len(kwargs["managed_agents"]), 1)
            self.assertEqual(kwargs["managed_agents"][0].name, "gatekeeper")
            self.assertIsInstance(kwargs["managed_agents"][0], _StrictGatekeeperWrapper)

    def test_loop_orchestrators_expose_named_gatekeeper(self):
        with patch(
            "bastirr.agents.screening_loop_orchestrator.create_single_study_gatekeeper_agent",
            return_value=_FakeNamedGatekeeper(),
        ), patch(
            "bastirr.agents.screening_loop_orchestrator.create_chunk_gatekeeper_agent",
            return_value=_FakeNamedGatekeeper(),
        ), patch("bastirr.agents.screening_loop_orchestrator.CodeAgent") as code_agent:
            from bastirr.agents.screening_loop_orchestrator import (
                create_screening_chunk_loop_orchestrator_agent,
                create_screening_loop_orchestrator_agent,
            )

            create_screening_loop_orchestrator_agent(MagicMock(), MagicMock())
            create_screening_chunk_loop_orchestrator_agent(MagicMock(), MagicMock())
            for call in code_agent.call_args_list:
                managed = call.kwargs["managed_agents"]
                self.assertEqual(managed[0].name, "gatekeeper")
                self.assertIsInstance(managed[0], _StrictGatekeeperWrapper)


def _make_review(n_studies: int = 2) -> SystematicReview:
    studies = [
        Study(title=f"Title {i}", abstract=f"Abstract {i}", label=1.0 if i == 1 else 0.0)
        for i in range(1, n_studies + 1)
    ]
    return SystematicReview(
        review_url="https://example.test/review",
        title="Synthetic Review",
        background="Background",
        objective="Objective",
        selection_criteria="Criteria",
        studies=studies,
    )


def _make_review_case(n_studies: int = 2) -> ScreeningBenchmarkReview:
    return ScreeningBenchmarkReview(
        key="synthetic_review",
        split="val",
        review_url="https://example.test/review",
        title="Synthetic Review",
        expected_n_studies=n_studies,
        expected_n_screen_pass=1,
        expected_n_screen_exclude=n_studies - 1,
    )


def _make_preset(key: str = "openai_gpt5") -> ResolvedModelPreset:
    preset = ResolvedModelPreset(
        key=key,
        description="test",
        display_name=key,
        backend="openai",
        model_id=key,
        api_base=None,
        api_key="test-key",
        api_key_source="OPENAI_API_KEY",
    )
    # Avoid constructing a real provider client in unit tests.
    object.__setattr__(
        preset,
        "create_model",
        lambda: MagicMock(name=f"{key}_model"),
    )
    return preset


class RunnerOverflowMappingTests(unittest.TestCase):
    def test_batch_runner_stops_on_overflow_without_retry(self):
        review = _make_review()
        review_case = _make_review_case()
        gatekeeper_model = _make_preset("gk")
        orchestrator_model = _make_preset("orch")
        call_count = {"n": 0}

        fake_orch = MagicMock()

        def _run(_task):
            call_count["n"] += 1
            raise ContextOverflowError("maximum context length exceeded")

        fake_orch.run.side_effect = _run

        with tempfile.TemporaryDirectory(dir=Path.cwd()) as tmpdir:
            output_root = Path(tmpdir)
            with patch(
                "bastirr.benchmarking.runner.load_review",
                return_value=review,
            ), patch(
                "bastirr.benchmarking.runner._validate_review_case",
            ), patch(
                "bastirr.benchmarking.runner.load_review_data",
            ), patch(
                "bastirr.benchmarking.runner.create_screening_orchestrator_agent",
                return_value=fake_orch,
            ):
                from bastirr.benchmarking.runner import run_screening_review

                result = run_screening_review(
                    suite_name="test",
                    review_case=review_case,
                    gatekeeper_model=gatekeeper_model,
                    orchestrator_model=orchestrator_model,
                    orchestrator_policy="fixed",
                    run_index=1,
                    output_root=output_root,
                    label_policy="include_label_0_5",
                )

        self.assertEqual(call_count["n"], 1)
        self.assertEqual(result["error_type"], "context_overflow")
        self.assertEqual(result["run_status"], "error")
        self.assertTrue(result["telemetry"]["context_overflow"])
        self.assertEqual(result["telemetry"]["context_overflow_count"], 1)

    def test_loop_runner_stops_resume_on_overflow(self):
        review = _make_review()
        review_case = _make_review_case()
        gatekeeper_model = _make_preset("gk")
        orchestrator_model = _make_preset("orch")
        call_count = {"n": 0}

        fake_orch = MagicMock()

        def _run(_task):
            call_count["n"] += 1
            raise ContextOverflowError("maximum context length exceeded")

        fake_orch.run.side_effect = _run

        with tempfile.TemporaryDirectory(dir=Path.cwd()) as tmpdir:
            output_root = Path(tmpdir)
            with patch(
                "bastirr.benchmarking.loop_runner.load_review",
                return_value=review,
            ), patch(
                "bastirr.benchmarking.loop_runner._validate_review_case",
            ), patch(
                "bastirr.benchmarking.loop_runner.load_review_data",
            ), patch(
                "bastirr.benchmarking.loop_runner.create_screening_loop_orchestrator_agent",
                return_value=fake_orch,
            ):
                from bastirr.benchmarking.loop_runner import run_screening_loop_review

                result = run_screening_loop_review(
                    suite_name="test",
                    review_case=review_case,
                    gatekeeper_model=gatekeeper_model,
                    orchestrator_model=orchestrator_model,
                    orchestrator_policy="fixed",
                    run_index=1,
                    output_root=output_root,
                    label_policy="include_label_0_5",
                )

        self.assertEqual(call_count["n"], 1)
        self.assertEqual(result["error_type"], "context_overflow")
        self.assertEqual(result["run_status"], "error")
        self.assertTrue(result["telemetry"]["context_overflow"])


if __name__ == "__main__":
    unittest.main()
