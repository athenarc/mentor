"""Context overflow must abort the pipeline and exit the CLI."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from smolagents import ActionStep

from mentor.cli import main
from mentor.errors import (
    ContextOverflowError,
    abort_on_classified_error,
    with_error_abort_callback,
)
from mentor.review import Criterion, SelectionCriteria, SystematicReview
from mentor.runtime.run import run_review


_SAMPLE_CRITERIA = SelectionCriteria(
    inclusion=[Criterion(id="IC1", text="Include RCTs")],
    exclusion=[Criterion(id="EC1", text="Exclude reviews")],
)


def _fake_session(tmp_dir: Path) -> SimpleNamespace:
    run_dir = Path(tmp_dir) / "run"
    run_dir.mkdir(parents=True, exist_ok=True)
    activity = MagicMock()
    activity.finalize.return_value = run_dir / "activity.md"
    agent_logger = MagicMock()
    model = SimpleNamespace(model_id="test-model")
    return SimpleNamespace(
        review=SystematicReview(
            title="T",
            background="B",
            objective="O",
            selection_criteria=_SAMPLE_CRITERIA,
            mode="screening-only",
            studies=[],
            prompts={},
        ),
        run_dir=run_dir,
        loggers=SimpleNamespace(
            activity_logger=activity,
            agent_logger=agent_logger,
        ),
        step_cbs={ActionStep: []},
        protocol_json="{}",
        backend="openai",
        activity_summary_model=model,
        models_by_role=None,
        models=model,
        profile_key="test",
    )


class RunReviewContextOverflowTests(unittest.TestCase):
    def test_run_review_wires_error_abort_callback(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            session = _fake_session(Path(tmpdir))
            orchestrator = MagicMock()
            orchestrator.run.return_value = "ok"
            captured: dict = {}

            def _capture_create(**kwargs):
                captured["step_callbacks"] = kwargs.get("step_callbacks")
                return orchestrator

            with (
                patch("mentor.runtime.run.prepare_run_session", return_value=session),
                patch(
                    "mentor.runtime.run.create_orchestrator_agent",
                    side_effect=_capture_create,
                ),
            ):
                run_review(
                    review_json_path="unused.json",
                    skip_activity_summary=True,
                    raise_on_error=False,
                )

            step_cbs = captured["step_callbacks"]
            self.assertIsInstance(step_cbs, dict)
            self.assertTrue(
                any(
                    getattr(cb, "_mentor_error_abort", False)
                    for cb in step_cbs[ActionStep]
                )
            )

    def test_run_review_records_error_and_reraises_context_overflow(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            session = _fake_session(Path(tmpdir))
            orchestrator = MagicMock()
            orchestrator.run.side_effect = ContextOverflowError(
                "context_overflow during agent 'gatekeeper' step 2: too long"
            )

            with (
                patch("mentor.runtime.run.prepare_run_session", return_value=session),
                patch(
                    "mentor.runtime.run.create_orchestrator_agent",
                    return_value=orchestrator,
                ),
                self.assertRaises(ContextOverflowError),
            ):
                run_review(
                    review_json_path="unused.json",
                    skip_activity_summary=True,
                    raise_on_error=True,
                )

            payload = json.loads((session.run_dir / "run.json").read_text(encoding="utf-8"))
            self.assertEqual(payload["status"], "error")
            self.assertIn("ContextOverflowError", payload["error"])

    def test_run_review_raise_on_error_false_still_marks_error(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            session = _fake_session(Path(tmpdir))
            orchestrator = MagicMock()
            orchestrator.run.side_effect = ContextOverflowError("overflow")

            with (
                patch("mentor.runtime.run.prepare_run_session", return_value=session),
                patch(
                    "mentor.runtime.run.create_orchestrator_agent",
                    return_value=orchestrator,
                ),
            ):
                result = run_review(
                    review_json_path="unused.json",
                    skip_activity_summary=True,
                    raise_on_error=False,
                )

            self.assertEqual(result, "")
            payload = json.loads((session.run_dir / "run.json").read_text(encoding="utf-8"))
            self.assertEqual(payload["status"], "error")


class CliContextOverflowExitTests(unittest.TestCase):
    def test_cli_exits_one_on_context_overflow(self):
        with patch(
            "mentor.cli.run_review",
            side_effect=ContextOverflowError("overflow"),
        ):
            with self.assertRaises(SystemExit) as ctx:
                main(
                    [
                        "--review",
                        "data/mentor/input/reviews/cotrimoxazole_hiv_cd003508.json",
                        "--model",
                        "dummy",
                        "--backend",
                        "openai",
                    ]
                )
        self.assertEqual(ctx.exception.code, 1)


class SoftStepOverflowAbortTests(unittest.TestCase):
    def test_wired_callback_raises_when_step_stores_overflow_error(self):
        callbacks = with_error_abort_callback({ActionStep: []})
        abort = next(
            cb for cb in callbacks[ActionStep] if getattr(cb, "_mentor_error_abort", False)
        )
        self.assertIs(abort, abort_on_classified_error)

        import httpx
        from openai import BadRequestError

        request = httpx.Request("POST", "https://example.test/v1/chat/completions")
        response = httpx.Response(400, request=request)
        step = ActionStep(step_number=1, timing=SimpleNamespace(start=0, end=0))
        step.error = BadRequestError(
            "Error code: 400",
            response=response,
            body={
                "error": {
                    "message": "This endpoint's maximum context length is 163840 tokens.",
                    "code": 400,
                }
            },
        )
        with self.assertRaises(ContextOverflowError):
            abort(step, agent=SimpleNamespace(name="gatekeeper"))


if __name__ == "__main__":
    unittest.main()
