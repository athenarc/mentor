"""
Hard-fail error handling for agent runs.

``abort_on_classified_error`` and related helpers turn selected provider
failures (notably context overflow) into raised exceptions so runners stop
instead of letting the orchestrator continue with partial step errors.
"""

from mentor.errors.abort import (
    CONTEXT_OVERFLOW_CLASSIFIER,
    DEFAULT_ERROR_CLASSIFIERS,
    ErrorClassifier,
    abort_on_classified_error,
    classify_error,
    make_error_abort_callback,
    with_error_abort_callback,
)
from mentor.errors.classification import is_context_overflow_error
from mentor.errors.exceptions import ContextOverflowError

__all__ = [
    "CONTEXT_OVERFLOW_CLASSIFIER",
    "DEFAULT_ERROR_CLASSIFIERS",
    "ContextOverflowError",
    "ErrorClassifier",
    "abort_on_classified_error",
    "classify_error",
    "is_context_overflow_error",
    "make_error_abort_callback",
    "with_error_abort_callback",
]
