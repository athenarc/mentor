"""
Tools used by the screening benchmark harness.

These helpers persist and format Gatekeeper-only outputs without relying on
the full end-to-end report/evidence path that expects Miner and Critic data.
"""

from __future__ import annotations

import json
import os

from smolagents import tool

from bastirr.tools.report_tools import _parse_decisions


@tool
def save_screening_evidence_json(
    screening_response: str,
    output_dir: str,
) -> str:
    """
    Save screening-only outputs in a screening-specific evidence.json shape.

    Args:
        screening_response: Raw response string from the Gatekeeper.
        output_dir: Directory where ``evidence.json`` should be written.

    Returns:
        A status string describing the saved file path.
    """
    result = {"screening_decisions": _parse_decisions(screening_response)}

    output_path = os.path.join(output_dir, "evidence.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    return f"Screening evidence saved to {output_path}"


@tool
def format_screening_summary(
    review_title: str,
    screening_response: str,
) -> str:
    """
    Build a short human-readable screening summary from Gatekeeper output.

    Args:
        review_title: Review title used in the summary heading.
        screening_response: Raw response string from the Gatekeeper.

    Returns:
        A short Markdown summary of the screening run.
    """
    decisions = _parse_decisions(screening_response)
    included = sum(
        1 for decision in decisions if decision.get("decision", "").upper() == "INCLUDE"
    )
    excluded = sum(
        1 for decision in decisions if decision.get("decision", "").upper() == "EXCLUDE"
    )

    if not decisions:
        return (
            f"# Screening Summary\n\n"
            f"- **Review:** {review_title}\n"
            f"- **Status:** No screening decisions could be parsed.\n"
        )

    return (
        f"# Screening Summary\n\n"
        f"- **Review:** {review_title}\n"
        f"- **Total decisions parsed:** {len(decisions)}\n"
        f"- **Included:** {included}\n"
        f"- **Excluded:** {excluded}\n"
    )
