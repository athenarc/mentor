"""
Step-callback helpers that abort agent runs on classified hard failures.

smolagents often stores managed-agent failures on ``ActionStep.error`` and
continues the orchestrator loop. These callbacks re-raise bastirr exceptions
so runners can fail fast instead of letting the LLM improvise recoveries.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass
from typing import Any

from smolagents import ActionStep
from smolagents.memory import MemoryStep

from bastirr.errors.classification import is_context_overflow_error
from bastirr.errors.exceptions import ContextOverflowError


@dataclass(frozen=True)
class ErrorClassifier:
    """Maps an observed step/call error onto a bastirr exception type."""

    name: str
    exception_type: type[Exception]
    matches: Callable[[Any], bool]


CONTEXT_OVERFLOW_CLASSIFIER = ErrorClassifier(
    name="context_overflow",
    exception_type=ContextOverflowError,
    matches=is_context_overflow_error,
)

DEFAULT_ERROR_CLASSIFIERS: tuple[ErrorClassifier, ...] = (CONTEXT_OVERFLOW_CLASSIFIER,)


def classify_error(
    exc_or_message: Any,
    classifiers: Sequence[ErrorClassifier] = DEFAULT_ERROR_CLASSIFIERS,
) -> ErrorClassifier | None:
    """Return the first matching classifier, or None."""
    for classifier in classifiers:
        if classifier.matches(exc_or_message):
            return classifier
    return None


def make_error_abort_callback(
    classifiers: Sequence[ErrorClassifier] = DEFAULT_ERROR_CLASSIFIERS,
) -> Callable[..., None]:
    """Build an ActionStep callback that aborts on any matching classifier."""
    classifiers = tuple(classifiers)

    def abort_on_classified_error(
        memory_step: MemoryStep,
        agent: Any = None,
        **kwargs: Any,
    ) -> None:
        if not isinstance(memory_step, ActionStep):
            return
        error = getattr(memory_step, "error", None)
        if error is None:
            return
        classifier = classify_error(error, classifiers)
        if classifier is None:
            return
        raise classifier.exception_type(
            f"{classifier.name} during agent "
            f"'{getattr(agent, 'name', 'unknown')}' "
            f"step {getattr(memory_step, 'step_number', '?')}: {error}"
        )

    abort_on_classified_error._bastirr_error_abort = True  # type: ignore[attr-defined]
    abort_on_classified_error._bastirr_error_classifiers = classifiers  # type: ignore[attr-defined]
    return abort_on_classified_error


# Default singleton used by screening orchestrators.
abort_on_classified_error = make_error_abort_callback()


def with_error_abort_callback(
    step_callbacks: list | dict | None,
    classifiers: Sequence[ErrorClassifier] | None = None,
) -> list | dict:
    """Return step_callbacks that include classified-error abort on ActionStep.

    Accepts either the list form used by some agents or the dict form
    produced by ``make_step_callbacks`` / ``attach_usage_collector``.

    Pass ``classifiers`` to abort on a custom set; omit it to use
    :data:`DEFAULT_ERROR_CLASSIFIERS` (currently context overflow only).
    """
    callback = (
        make_error_abort_callback(classifiers)
        if classifiers is not None
        else abort_on_classified_error
    )

    if step_callbacks is None:
        return [callback]

    if isinstance(step_callbacks, dict):
        existing = step_callbacks.get(ActionStep, [])
        if not isinstance(existing, list):
            existing = [existing] if existing else []
        if _has_error_abort(existing):
            return step_callbacks
        return {**step_callbacks, ActionStep: [*existing, callback]}

    callbacks = list(step_callbacks)
    if not _has_error_abort(callbacks):
        callbacks.append(callback)
    return callbacks


def _has_error_abort(callbacks: list) -> bool:
    return any(getattr(callback, "_bastirr_error_abort", False) for callback in callbacks)
