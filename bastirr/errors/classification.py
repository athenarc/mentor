"""Classify provider/agent failures into bastirr error types."""

from __future__ import annotations

from typing import Any

from bastirr.errors.exceptions import ContextOverflowError

_OVERFLOW_CODE = "context_length_exceeded"


def is_context_overflow_error(exc_or_message: Any) -> bool:
    """Return True if the value is a structured context-overflow failure.

    Matches only exception objects (and their ``__cause__`` / ``__context__``
    chain) using provider fields:

    - ``exc.code == "context_length_exceeded"`` (OpenAI-style)
    - ``exc.body`` / ``exc.body["error"]`` with that semantic code
    - ``exc.status_code == 400`` with a structured body message that reports
      maximum context length (OpenRouter-style nested ``error`` objects)

    Strings and other non-exception values never match. Flattened step-error
    text is intentionally not parsed.
    """
    if isinstance(exc_or_message, ContextOverflowError):
        return True
    if not isinstance(exc_or_message, BaseException):
        return False
    for exc in _iter_exception_chain(exc_or_message):
        if isinstance(exc, ContextOverflowError):
            return True
        if _exception_has_structured_overflow(exc):
            return True
    return False


def _iter_exception_chain(exc: BaseException):
    seen: set[int] = set()
    current: BaseException | None = exc
    while current is not None and id(current) not in seen:
        yield current
        seen.add(id(current))
        current = current.__cause__ or current.__context__


def _exception_has_structured_overflow(exc: BaseException) -> bool:
    code = getattr(exc, "code", None)
    if _is_overflow_code(code):
        return True

    body = getattr(exc, "body", None)
    if _body_has_overflow_code(body):
        return True

    status_code = getattr(exc, "status_code", None)
    if status_code == 400 and _body_has_context_length_message(body):
        return True
    return False


def _is_overflow_code(code: Any) -> bool:
    return isinstance(code, str) and code.lower() == _OVERFLOW_CODE


def _body_has_overflow_code(body: Any) -> bool:
    if not isinstance(body, dict):
        return False
    if _is_overflow_code(body.get("code")):
        return True
    nested = body.get("error")
    if isinstance(nested, dict) and _is_overflow_code(nested.get("code")):
        return True
    return False


def _body_has_context_length_message(body: Any) -> bool:
    """True when a structured body message reports max context length."""
    if not isinstance(body, dict):
        return False
    messages: list[str] = []
    message = body.get("message")
    if isinstance(message, str):
        messages.append(message)
    nested = body.get("error")
    if isinstance(nested, dict):
        nested_message = nested.get("message")
        if isinstance(nested_message, str):
            messages.append(nested_message)
    return any("maximum context length" in msg.lower() for msg in messages)
