"""
Screening batch helpers for the Orchestrator.

``get_screening_batches`` plans resume-aware batches (payloads for the managed
Gatekeeper). ``append_screening_batch`` and ``get_screening_response_json``
persist and reload decisions. The Orchestrator calls Gatekeeper once per batch.
"""

from __future__ import annotations

import json
import logging
from typing import Any

from smolagents import Tool, tool

from mentor.tools.search.search_tools import (
    _candidate_studies_batch_payload,
    _resolve_studies,
)
from mentor.tools.screening_persistence import (
    append_batch_decisions,
    batch_indices,
    decisions_to_screening_response,
    read_existing_decisions,
)

logger = logging.getLogger("mentor.screening_loop")


class GetScreeningBatchesTool(Tool):
    """Plan remaining screening batches for the managed Gatekeeper."""

    name = "get_screening_batches"
    description = (
        "Return a JSON array of remaining screening batches. Each item has "
        "'indices' (study indices for that batch) and 'payload' (the object "
        "to pass as additional_args['screening_payload'] to gatekeeper). "
        "Skips studies already saved in evidence.json. Call with output_dir; "
        "batch size is fixed when the tool is created (None = one batch)."
    )
    inputs = {
        "output_dir": {
            "type": "string",
            "description": "Run output directory containing evidence.json (for resume).",
        },
    }
    output_type = "string"

    def __init__(self, *, batch_size: int | None = None) -> None:
        super().__init__()
        if batch_size is not None and batch_size < 1:
            raise ValueError("batch_size must be at least 1 when provided")
        self.batch_size = batch_size

    def forward(self, output_dir: str) -> str:
        studies = _resolve_studies()
        if not studies:
            raise ValueError(
                "No candidate studies available. Load review data or run the "
                "librarian before calling get_screening_batches."
            )
        expected_n = len(studies)
        existing = read_existing_decisions(output_dir)
        completed = {
            int(d.get("study_index", 0))
            for d in existing
            if str(d.get("study_index", "")).isdigit() and int(d.get("study_index", 0)) >= 1
        }
        missing = [i for i in range(1, expected_n + 1) if i not in completed]
        batches = batch_indices(missing, batch_size=self.batch_size)

        if not batches:
            logger.info(
                "get_screening_batches: all %s studies already decided",
                expected_n,
            )
            return "[]"

        logger.info(
            "get_screening_batches: %s studies remaining in %s batch(es) (batch_size=%s)",
            len(missing),
            len(batches),
            self.batch_size,
        )

        items: list[dict[str, Any]] = []
        for batch in batches:
            payload_json = _candidate_studies_batch_payload(json.dumps(batch))
            items.append(
                {
                    "indices": list(batch),
                    "payload": json.loads(payload_json),
                }
            )
        return json.dumps(items, ensure_ascii=False)


def make_get_screening_batches_tool(*, batch_size: int | None = None) -> GetScreeningBatchesTool:
    """Build ``get_screening_batches`` with a fixed ``batch_size``."""
    return GetScreeningBatchesTool(batch_size=batch_size)


@tool
def append_screening_batch(
    screening_response: str,
    output_dir: str,
    expected_indices_json: str,
    expected_n_studies: int,
) -> str:
    """
    Validate a Gatekeeper batch response and append decisions to evidence.json.

    Call immediately after each gatekeeper(...) call. Do not accumulate batch
    responses in Orchestrator memory.

    Args:
        screening_response: Raw Gatekeeper response string for this batch.
        output_dir: Run output directory for evidence.json.
        expected_indices_json: JSON array of study indices for this batch.
        expected_n_studies: Total studies expected for the full screening run.

    Returns:
        Short confirmation with completed decision count.
    """
    try:
        raw_indices = json.loads(expected_indices_json)
    except json.JSONDecodeError as exc:
        raise ValueError("expected_indices_json must be a JSON array of integers.") from exc
    if not isinstance(raw_indices, list) or not raw_indices:
        raise ValueError("expected_indices_json must be a non-empty JSON array.")
    indices: list[int] = []
    for raw in raw_indices:
        try:
            indices.append(int(raw))
        except (TypeError, ValueError) as exc:
            raise ValueError(f"Invalid study index in expected_indices_json: {raw!r}") from exc

    updated = append_batch_decisions(
        screening_response,
        output_dir,
        indices,
        expected_n_studies=int(expected_n_studies),
    )
    return (
        f"Saved {len(indices)} decision(s); "
        f"{len(updated)}/{int(expected_n_studies)} total in {output_dir}."
    )


@tool
def get_screening_response_json(output_dir: str) -> str:
    """
    Load saved screening decisions and return a Gatekeeper-shaped JSON string.

    Use after all batches are appended (full pipeline) before
    extract_included_studies.

    Args:
        output_dir: Directory containing evidence.json.

    Returns:
        JSON string with n_total / n_included / n_excluded / decisions.
    """
    decisions = read_existing_decisions(output_dir)
    if not decisions:
        raise ValueError(f"No screening decisions found in {output_dir}")
    return decisions_to_screening_response(decisions)
