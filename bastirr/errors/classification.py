"""Classify provider/agent failure strings into bastirr error types."""

from __future__ import annotations

import re
from typing import Any

from bastirr.errors.exceptions import ContextOverflowError

# Strong message from OpenRouter / OpenAI-compatible overflow bodies in our logs.
_OVERFLOW_MESSAGE = re.compile(r"maximum context length", re.I)
# HTTP 400 appears as "Error code: 400" and/or "'code': 400" in stringified errors.
_HTTP_400 = re.compile(
    r"(?:Error code:\s*400\b|['\"]code['\"]\s*:\s*400\b)",
    re.I,
)
# OpenAI-style semantic code when present (sufficient on its own).
_OVERFLOW_SEMANTIC_CODE = re.compile(r"context_length_exceeded", re.I)


def is_context_overflow_error(exc_or_message: Any) -> bool:
    """Return True if the exception/message indicates a context overflow.

    Prefers structured signals when present. For OpenRouter-style stringified
    errors, requires both ``maximum context length`` and HTTP 400 — not either
    alone (400 is shared by many bad requests; the phrase alone can appear in
    unrelated text).
    """
    if isinstance(exc_or_message, ContextOverflowError):
        return True
    text = str(exc_or_message or "")
    if not text:
        return False
    if _OVERFLOW_SEMANTIC_CODE.search(text):
        return True
    return bool(_OVERFLOW_MESSAGE.search(text) and _HTTP_400.search(text))
