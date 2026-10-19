"""
Run session setup for pipeline and benchmark entrypoints.

``prepare_run_session`` wires dataset load, logging, models, and the study
store. ``review_to_json`` / ``protocol_to_json`` format reviews for agents.
Default LLM profiles live in ``profiles.json`` beside this package.
"""

from mentor.runtime.session import (
    RunLoggers,
    RunSession,
    prepare_run_session,
    protocol_to_json,
    review_to_json,
)

__all__ = [
    "review_to_json",
    "protocol_to_json",
    "RunLoggers",
    "RunSession",
    "prepare_run_session",
]
