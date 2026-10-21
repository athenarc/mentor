"""
Run session setup and public run API for Mentor entrypoints.

Prefer ``from mentor.runtime.run import run_review`` for the in-process API
(avoids pulling agent imports when only resolving profiles).
Model catalogue and profiles live in ``mentor/config/model_profiles.json``.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from mentor.runtime.session import (
    RunLoggers,
    RunSession,
    prepare_run_session,
    protocol_to_json,
    review_to_json,
)

if TYPE_CHECKING:
    from mentor.runtime.run import run_review as run_review

__all__ = [
    "review_to_json",
    "protocol_to_json",
    "RunLoggers",
    "RunSession",
    "prepare_run_session",
    "run_review",
]


def __getattr__(name: str) -> Any:
    if name == "run_review":
        from mentor.runtime.run import run_review as _run_review

        return _run_review
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
