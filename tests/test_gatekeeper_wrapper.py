"""Unit tests for strict gatekeeper wrapper and context-overflow fail-fast."""

from __future__ import annotations

import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from smolagents import ActionStep

from mentor.agents.wrappers import (
    GATEKEEPER_PAYLOAD_KEY,
    GATEKEEPER_TASK,
    wrap_gatekeeper,
)
from mentor.agents.wrappers.gatekeeper import _StrictGatekeeperWrapper
from mentor.errors import (
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


def _openai_bad_request(*, status_code: int = 400, body: dict):
    import httpx
    from openai import BadRequestError

    request = httpx.Request("POST", "https://example.test/v1/chat/completions")
    response = httpx.Response(status_code, request=request)
    return BadRequestError("Error code: 400", response=response, body=body)


class ContextOverflowClassificationTests(unittest.TestCase):
    def test_detects_structured_openai_semantic_code(self):
        exc = _openai_bad_request(
            body={
                "message": "too long",
                "type": "invalid_request_error",
                "code": "context_length_exceeded",
            }
        )
        self.assertTrue(is_context_overflow_error(exc))

    def test_detects_structured_openrouter_nested_body(self):
        exc = _openai_bad_request(
            body={
                "error": {
                    "message": (
                        "This endpoint's maximum context length is 163840 tokens."
                    ),
                    "code": 400,
                }
            }
        )
        self.assertTrue(is_context_overflow_error(exc))

    def test_detects_structured_overflow_via_exception_cause(self):
        cause = _openai_bad_request(
            body={
                "message": "too long",
                "code": "context_length_exceeded",
            }
        )
        wrapped = RuntimeError("Error in generating model output")
        wrapped.__cause__ = cause
        self.assertTrue(is_context_overflow_error(wrapped))

    def test_ignores_structured_400_without_overflow_markers(self):
        exc = _openai_bad_request(
            body={"error": {"message": "bad json", "code": 400}}
        )
        self.assertFalse(is_context_overflow_error(exc))

    def test_ignores_flattened_error_strings(self):
        self.assertFalse(
            is_context_overflow_error(
                "Error code: 400 - {'error': {'message': "
                "\"This endpoint's maximum context length is 163840 tokens.\", "
                "'code': 400}}"
            )
        )
        self.assertFalse(
            is_context_overflow_error(
                "Error code: 400 - {'error': {'message': 'too long', "
                "'code': 'context_length_exceeded'}}"
            )
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
            fixed_task=GATEKEEPER_TASK,
        )
        payload = {"studies": [_study_payload()]}
        result = wrapped(
            "LLM wrote a huge task with study JSON here",
            additional_args={GATEKEEPER_PAYLOAD_KEY: payload},
        )

        self.assertEqual(result, "ok")
        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0]["task"], GATEKEEPER_TASK)
        self.assertEqual(
            calls[0]["additional_args"][GATEKEEPER_PAYLOAD_KEY],
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
            fixed_task=GATEKEEPER_TASK,
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
            fixed_task=GATEKEEPER_TASK,
        )
        with self.assertRaises(ValueError):
            wrapped(
                "screen",
                additional_args={
                    GATEKEEPER_PAYLOAD_KEY: {"study_indices": [1, 2, 3]},
                },
            )
        self.assertEqual(calls, [])

    def test_rejects_mixed_studies_list(self):
        calls = []

        class FakeAgent:
            name = "gatekeeper"

            def __call__(self, *args, **kwargs):
                calls.append((args, kwargs))
                return "ok"

        wrapped = wrap_gatekeeper(FakeAgent(), fixed_task=GATEKEEPER_TASK)
        with self.assertRaises(ValueError):
            wrapped(
                "screen",
                additional_args={
                    GATEKEEPER_PAYLOAD_KEY: {
                        "studies": [
                            _study_payload(),
                            {"study_index": 2, "title": "missing abstract"},
                        ],
                    },
                },
            )
        self.assertEqual(calls, [])

    def test_overflow_exception_becomes_context_overflow_error(self):
        class OverflowAgent:
            name = "gatekeeper"

            def __call__(self, task="", additional_args=None, **kwargs):
                raise _openai_bad_request(
                    body={
                        "error": {
                            "message": (
                                "This endpoint's maximum context length is "
                                "163840 tokens."
                            ),
                            "code": 400,
                        }
                    }
                )

        wrapped = wrap_gatekeeper(
            OverflowAgent(),
            fixed_task=GATEKEEPER_TASK,
        )
        with self.assertRaises(ContextOverflowError):
            wrapped(
                "ignored",
                additional_args={
                    GATEKEEPER_PAYLOAD_KEY: {"studies": [_study_payload()]},
                },
            )


class OverflowAbortCallbackTests(unittest.TestCase):
    def test_abort_callback_raises_on_overflow_step_error(self):
        step = ActionStep(step_number=2, timing=SimpleNamespace(start=0, end=0))
        step.error = _openai_bad_request(
            body={
                "error": {
                    "message": (
                        "This endpoint's maximum context length is 262144 tokens."
                    ),
                    "code": 400,
                }
            }
        )
        with self.assertRaises(ContextOverflowError):
            abort_on_classified_error(step, agent=SimpleNamespace(name="orchestrator"))

    def test_abort_callback_ignores_flattened_overflow_strings(self):
        step = ActionStep(step_number=2, timing=SimpleNamespace(start=0, end=0))
        step.error = (
            "Error code: 400 - {'error': {'message': "
            "\"This endpoint's maximum context length is 262144 tokens.\", 'code': 400}}"
        )
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


class OrchestratorScreeningToolTests(unittest.TestCase):
    def test_screening_stage_has_no_managed_agents_and_screen_candidates_tool(self):
        with patch(
            "mentor.agents.orchestrator.create_gatekeeper_agent",
            return_value=_FakeNamedGatekeeper(),
        ), patch(
            "mentor.agents.orchestrator.CodeAgent",
        ) as code_agent:
            from mentor.agents.orchestrator import create_orchestrator_agent

            create_orchestrator_agent(
                MagicMock(),
                stages="screening",
                batch_size=1,
                output_dir="/tmp/out",
            )
            kwargs = code_agent.call_args.kwargs
            self.assertEqual(kwargs["managed_agents"], [])
            tool_names = [getattr(t, "name", None) for t in kwargs["tools"]]
            self.assertIn("screen_candidates", tool_names)

    def test_full_stage_excludes_gatekeeper_from_managed_agents(self):
        with patch(
            "mentor.agents.orchestrator.create_gatekeeper_agent",
            return_value=_FakeNamedGatekeeper(),
        ), patch(
            "mentor.agents.orchestrator.create_librarian_agent",
            return_value=MagicMock(name="librarian"),
        ), patch(
            "mentor.agents.orchestrator.create_miner_agent",
            return_value=MagicMock(name="miner"),
        ), patch(
            "mentor.agents.orchestrator.create_critic_agent",
            return_value=MagicMock(name="critic"),
        ), patch(
            "mentor.agents.orchestrator.CodeAgent",
        ) as code_agent:
            from mentor.agents.orchestrator import create_orchestrator_agent

            create_orchestrator_agent(
                MagicMock(),
                stages="full",
                batch_size=None,
                output_dir="/tmp/out",
            )
            kwargs = code_agent.call_args.kwargs
            managed_names = [getattr(a, "name", None) for a in kwargs["managed_agents"]]
            self.assertNotIn("gatekeeper", managed_names)
            tool_names = [getattr(t, "name", None) for t in kwargs["tools"]]
            self.assertIn("screen_candidates", tool_names)


if __name__ == "__main__":
    unittest.main()
