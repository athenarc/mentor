"""Bastirr exceptions and hard-fail error handling helpers."""

from bastirr.errors.abort import (
    CONTEXT_OVERFLOW_CLASSIFIER,
    DEFAULT_ERROR_CLASSIFIERS,
    ErrorClassifier,
    abort_on_classified_error,
    classify_error,
    make_error_abort_callback,
    with_error_abort_callback,
)
from bastirr.errors.classification import is_context_overflow_error
from bastirr.errors.exceptions import ContextOverflowError

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
