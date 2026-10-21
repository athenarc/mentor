"""
Python-driven screening batch loop exposed as a smolagents tool.

``make_screen_candidates_tool`` returns a tool that chunks candidates,
calls the wrapped Gatekeeper once per batch, validates and persists
decisions, and returns a merged Gatekeeper-shaped JSON string.
"""

from __future__ import annotations

import json
import logging
from typing import Any

from smolagents import Tool

from mentor.tools.search.search_tools import (
    _candidate_studies_chunk_payload,
    _resolve_studies,
)
from mentor.tools.screening_persistence import (
    append_chunk_decisions,
    chunk_indices,
    decisions_to_screening_response,
    read_existing_decisions,
)
from mentor.agents.wrappers.gatekeeper import GATEKEEPER_PAYLOAD_KEY

logger = logging.getLogger("mentor.screening_loop")


def _agent_response_text(result: Any) -> str:
    if result is None:
        return ""
    if isinstance(result, str):
        return result
    return str(result)


class ScreenCandidatesTool(Tool):
    """Run Gatekeeper screening over all (remaining) candidates in batches."""

    name = "screen_candidates"
    description = (
        "Screen all candidate studies via the Gatekeeper in bounded batches. "
        "Persists decisions to evidence.json incrementally and returns a "
        "merged Gatekeeper-shaped JSON string with one decision per study. "
        "Call with no arguments; batch size and output directory are fixed "
        "when the tool is created."
    )
    inputs: dict = {}
    output_type = "string"

    def __init__(
        self,
        gatekeeper: Any,
        *,
        batch_size: int | None = None,
        output_dir: str,
        max_batch_attempts: int = 2,
    ) -> None:
        super().__init__()
        if batch_size is not None and batch_size < 1:
            raise ValueError("batch_size must be at least 1 when provided")
        if max_batch_attempts < 1:
            raise ValueError("max_batch_attempts must be at least 1")
        self.gatekeeper = gatekeeper
        self.batch_size = batch_size
        self.output_dir = str(output_dir)
        self.max_batch_attempts = max_batch_attempts

    def forward(self) -> str:
        studies = _resolve_studies()
        if not studies:
            raise ValueError(
                "No candidate studies available. Load review data or run the "
                "librarian before calling screen_candidates."
            )
        expected_n = len(studies)
        existing = read_existing_decisions(self.output_dir)
        completed = {
            int(d.get("study_index", 0))
            for d in existing
            if str(d.get("study_index", "")).isdigit() and int(d.get("study_index", 0)) >= 1
        }
        missing = [i for i in range(1, expected_n + 1) if i not in completed]
        batches = chunk_indices(missing, chunk_size=self.batch_size)

        if not batches:
            logger.info(
                "screen_candidates: all %s studies already decided; returning saved evidence",
                expected_n,
            )
            return decisions_to_screening_response(existing)

        logger.info(
            "screen_candidates: %s studies remaining in %s batch(es) (batch_size=%s)",
            len(missing),
            len(batches),
            self.batch_size,
        )

        for batch_number, batch in enumerate(batches, start=1):
            last_error: Exception | None = None
            for attempt in range(1, self.max_batch_attempts + 1):
                try:
                    payload = _candidate_studies_chunk_payload(json.dumps(batch))
                    raw = self.gatekeeper(
                        "",
                        additional_args={GATEKEEPER_PAYLOAD_KEY: payload},
                    )
                    response_text = _agent_response_text(raw)
                    append_chunk_decisions(
                        response_text,
                        self.output_dir,
                        batch,
                        expected_n_studies=expected_n,
                    )
                    last_error = None
                    break
                except Exception as exc:
                    last_error = exc
                    logger.warning(
                        "screen_candidates: batch %s/%s attempt %s/%s failed "
                        "(indices=%s): %s",
                        batch_number,
                        len(batches),
                        attempt,
                        self.max_batch_attempts,
                        batch,
                        exc,
                    )
            if last_error is not None:
                raise ValueError(
                    f"Gatekeeper failed for batch {batch_number}/{len(batches)} "
                    f"(indices={batch}) after {self.max_batch_attempts} attempt(s): "
                    f"{last_error}"
                ) from last_error

        final = read_existing_decisions(self.output_dir)
        if len(final) != expected_n:
            raise ValueError(
                f"Incomplete screening after batch loop: expected {expected_n} "
                f"decisions, found {len(final)}."
            )
        return decisions_to_screening_response(final)


def make_screen_candidates_tool(
    gatekeeper: Any,
    *,
    batch_size: int | None = None,
    output_dir: str,
    max_batch_attempts: int = 2,
) -> ScreenCandidatesTool:
    """Build the ``screen_candidates`` tool bound to a wrapped Gatekeeper."""
    return ScreenCandidatesTool(
        gatekeeper,
        batch_size=batch_size,
        output_dir=output_dir,
        max_batch_attempts=max_batch_attempts,
    )
