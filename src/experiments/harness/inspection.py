"""
Inspection artifacts for Gatekeeper screening benchmark runs.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments.harness.metrics import (
    describe_screening_label_policy,
    gold_label_to_screening_decision,
    gold_screening_policy_mapping,
)
from mentor.config import (
    LABEL_EXCLUDED_FULLTEXT,
    LABEL_EXCLUDED_SCREENING,
    LABEL_INCLUDED,
)


def gold_label_to_review_outcome(label: float) -> str:
    """Map the raw dataset label to the final-review disposition."""
    numeric_label = float(label)
    if numeric_label == LABEL_INCLUDED:
        return "included_in_review"
    if numeric_label == LABEL_EXCLUDED_FULLTEXT:
        return "excluded_after_full_text"
    if numeric_label == LABEL_EXCLUDED_SCREENING:
        return "excluded_at_screening"
    return "unknown"


def _normalize_screening_decisions(
    screening_decisions: list[dict],
    *,
    max_study_index: int,
) -> dict[int, dict]:
    """Return the last valid parsed decision for each study index."""
    decision_by_index: dict[int, dict] = {}

    for decision in screening_decisions:
        try:
            study_index = int(decision.get("study_index", 0))
        except (TypeError, ValueError):
            continue

        if study_index < 1 or study_index > max_study_index:
            continue

        predicted_decision = str(decision.get("decision", "")).upper()
        if predicted_decision not in {"INCLUDE", "EXCLUDE"}:
            continue

        reason = (
            str(decision.get("reason", "")).strip()
            or str(decision.get("rationale", "")).strip()
        )

        decision_by_index[study_index] = {
            "study_index": study_index,
            "predicted_decision": predicted_decision,
            "predicted_reason": reason,
        }

    return decision_by_index


def build_screening_inspection_payload(
    review,
    screening_decisions: list[dict],
    metrics: dict,
) -> dict:
    """Build a study-by-study gold-vs-prediction inspection payload."""
    label_policy = metrics.get("gold_label_policy", "include_label_0_5")
    decision_by_index = _normalize_screening_decisions(
        screening_decisions,
        max_study_index=len(review.studies),
    )

    studies: list[dict] = []
    for study_index, study in enumerate(review.studies, start=1):
        gold_decision = gold_label_to_screening_decision(
            study.label,
            label_policy=label_policy,
        )
        gold_review_outcome = gold_label_to_review_outcome(study.label)
        predicted = decision_by_index.get(study_index)
        predicted_decision = predicted["predicted_decision"] if predicted else ""
        predicted_reason = predicted["predicted_reason"] if predicted else ""

        if not predicted_decision:
            match_status = "missing"
            prediction_matches_gold = False
        else:
            prediction_matches_gold = predicted_decision == gold_decision
            match_status = "correct" if prediction_matches_gold else "incorrect"

        studies.append({
            "study_index": study_index,
            "study_title": study.title,
            "gold_label": float(study.label),
            "gold_screening_decision": gold_decision,
            "gold_review_outcome": gold_review_outcome,
            "predicted_decision": predicted_decision,
            "predicted_reason": predicted_reason,
            "prediction_matches_gold": prediction_matches_gold,
            "match_status": match_status,
        })

    match_count = sum(1 for study in studies if study["match_status"] == "correct")
    mismatch_count = sum(1 for study in studies if study["match_status"] == "incorrect")
    missing_count = sum(1 for study in studies if study["match_status"] == "missing")

    return {
        "review_title": review.title,
        "review_url": review.review_url,
        "screening_criteria": review.selection_criteria,
        "gold_label_policy": label_policy,
        "gold_label_policy_description": describe_screening_label_policy(label_policy),
        "gold_screening_policy": gold_screening_policy_mapping(label_policy),
        "summary": {
            "n_studies": metrics["n_studies"],
            "gold_pass_count": metrics["gold_pass_count"],
            "gold_exclude_count": metrics["gold_exclude_count"],
            "predicted_pass_count": metrics["predicted_pass_count"],
            "predicted_exclude_count": metrics["predicted_exclude_count"],
            "tp": metrics["tp"],
            "fp": metrics["fp"],
            "tn": metrics["tn"],
            "fn": metrics["fn"],
            "match_count": match_count,
            "mismatch_count": mismatch_count,
            "missing_decision_count": missing_count,
            "duplicate_decision_count": metrics["duplicate_decision_count"],
            "invalid_decision_count": metrics["invalid_decision_count"],
        },
        "studies": studies,
    }


def _preview_text(text: str, *, max_chars: int = 120) -> str:
    compact = " ".join(text.split())
    if len(compact) <= max_chars:
        return compact
    return compact[: max_chars - 3] + "..."


def _escape_markdown_cell(text: str) -> str:
    return text.replace("|", "\\|").replace("\n", " ").strip()


def _write_screening_inspection_markdown(output_path: Path, payload: dict) -> None:
    studies = payload["studies"]
    mismatches = [
        study
        for study in studies
        if study["match_status"] in {"incorrect", "missing"}
    ]
    summary = payload["summary"]

    lines = [
        "# Screening Inspection",
        "",
        f"- **Review:** {payload['review_title']}",
        f"- **Review URL:** {payload['review_url']}",
        f"- **Screening criteria:** {_escape_markdown_cell(payload['screening_criteria'])}",
        f"- **Gold label policy:** `{payload['gold_label_policy']}`",
        f"- **Gold screening rule:** {payload['gold_label_policy_description']}.",
        f"- **Matches:** {summary['match_count']} / {summary['n_studies']}",
        f"- **Mismatches:** {summary['mismatch_count']}",
        f"- **Missing decisions:** {summary['missing_decision_count']}",
        "",
        "## Mismatches",
        "",
    ]

    if not mismatches:
        lines.append("All studies matched the gold screening decision.")
    else:
        lines.extend([
            "| Index | Predicted | Gold | Gold Outcome | Title | Agent Rationale |",
            "|-------|-----------|------|--------------|-------|-----------------|",
        ])
        for study in mismatches:
            lines.append(
                "| {study_index} | {predicted} | {gold} | {outcome} | {title} | {reason} |".format(
                    study_index=study["study_index"],
                    predicted=study["predicted_decision"] or "MISSING",
                    gold=study["gold_screening_decision"],
                    outcome=study["gold_review_outcome"],
                    title=_escape_markdown_cell(study["study_title"]),
                    reason=_escape_markdown_cell(
                        _preview_text(study["predicted_reason"]) or "—"
                    ),
                )
            )

    lines.extend([
        "",
        "## All Studies",
        "",
        "| Index | Predicted | Gold | Match | Gold Outcome | Title |",
        "|-------|-----------|------|-------|--------------|-------|",
    ])
    for study in studies:
        lines.append(
            "| {study_index} | {predicted} | {gold} | {status} | {outcome} | {title} |".format(
                study_index=study["study_index"],
                predicted=study["predicted_decision"] or "MISSING",
                gold=study["gold_screening_decision"],
                status=study["match_status"],
                outcome=study["gold_review_outcome"],
                title=_escape_markdown_cell(study["study_title"]),
            )
        )

    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_screening_inspection_artifacts(
    *,
    run_dir: Path,
    review,
    screening_decisions: list[dict],
    metrics: dict,
) -> dict[str, str]:
    """Write inspection JSON and Markdown artifacts for one benchmark run."""
    payload = build_screening_inspection_payload(
        review=review,
        screening_decisions=screening_decisions,
        metrics=metrics,
    )

    json_path = run_dir / "screening_inspection.json"
    markdown_path = run_dir / "screening_inspection.md"

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    _write_screening_inspection_markdown(markdown_path, payload)

    return {
        "screening_inspection_json": str(json_path),
        "screening_inspection_markdown": str(markdown_path),
    }
