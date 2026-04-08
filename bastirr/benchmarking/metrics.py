"""
Metrics for Gatekeeper title/abstract screening benchmarks.
"""

from __future__ import annotations

from typing import Iterable

from bastirr.config import (
    LABEL_EXCLUDED_FULLTEXT,
    LABEL_EXCLUDED_SCREENING,
    LABEL_INCLUDED,
)


SCREENING_LABEL_POLICIES = ("include_label_0_5", "exclude_label_0_5")


def validate_screening_label_policy(label_policy: str) -> str:
    """Validate and normalize the benchmark gold-label policy name."""
    if label_policy not in SCREENING_LABEL_POLICIES:
        raise ValueError(
            "Unknown screening label policy "
            f"'{label_policy}'. Available policies: {', '.join(SCREENING_LABEL_POLICIES)}"
        )
    return label_policy


def describe_screening_label_policy(label_policy: str) -> str:
    """Return a human-readable description of the gold-label mapping."""
    validated = validate_screening_label_policy(label_policy)
    if validated == "include_label_0_5":
        return "dataset labels 1.0 and 0.5 count as INCLUDE; 0.0 counts as EXCLUDE"
    return "dataset label 1.0 counts as INCLUDE; 0.5 and 0.0 count as EXCLUDE"


def gold_screening_policy_mapping(label_policy: str) -> dict[str, str]:
    """Return the explicit label-to-decision mapping for the selected policy."""
    validated = validate_screening_label_policy(label_policy)
    if validated == "include_label_0_5":
        return {
            "1.0": "INCLUDE",
            "0.5": "INCLUDE",
            "0.0": "EXCLUDE",
        }
    return {
        "1.0": "INCLUDE",
        "0.5": "EXCLUDE",
        "0.0": "EXCLUDE",
    }


def gold_label_to_screening_decision(
    label: float,
    *,
    label_policy: str = "include_label_0_5",
) -> str:
    """
    Map dataset labels to title/abstract screening ground truth.

    The default ``include_label_0_5`` policy treats labels ``1.0`` and ``0.5``
    as ``INCLUDE``. The alternate ``exclude_label_0_5`` policy treats only
    ``1.0`` as ``INCLUDE``.
    """
    validated = validate_screening_label_policy(label_policy)
    numeric_label = float(label)

    if numeric_label == LABEL_INCLUDED:
        return "INCLUDE"
    if numeric_label == LABEL_EXCLUDED_FULLTEXT:
        return "INCLUDE" if validated == "include_label_0_5" else "EXCLUDE"
    if numeric_label == LABEL_EXCLUDED_SCREENING:
        return "EXCLUDE"
    return "INCLUDE" if numeric_label >= 0.5 else "EXCLUDE"


def _safe_divide(numerator: float, denominator: float) -> float | None:
    if denominator == 0:
        return None
    return numerator / denominator


def _normalize_decisions(
    screening_decisions: Iterable[dict],
    *,
    max_study_index: int,
) -> tuple[dict[int, str], int, int]:
    """
    Normalize parsed screening decisions into an index-to-label map.

    Returns:
        ``(decision_by_index, duplicate_count, invalid_count)``
    """
    decision_by_index: dict[int, str] = {}
    duplicate_count = 0
    invalid_count = 0

    for decision in screening_decisions:
        try:
            study_index = int(decision.get("study_index", 0))
        except (TypeError, ValueError):
            invalid_count += 1
            continue

        if study_index < 1 or study_index > max_study_index:
            invalid_count += 1
            continue

        label = str(decision.get("decision", "")).upper()
        if label not in {"INCLUDE", "EXCLUDE"}:
            invalid_count += 1
            continue

        if study_index in decision_by_index:
            duplicate_count += 1
        decision_by_index[study_index] = label

    return decision_by_index, duplicate_count, invalid_count


def compute_screening_metrics(
    review,
    screening_decisions: list[dict],
    *,
    label_policy: str = "include_label_0_5",
) -> dict:
    """
    Compute study-level screening metrics for one benchmark run.

    Missing study decisions are treated as not passing screening when building
    confusion metrics, and are reported separately via coverage/missing counts.
    """
    validated_policy = validate_screening_label_policy(label_policy)
    gold_by_index = {
        index: gold_label_to_screening_decision(
            study.label,
            label_policy=validated_policy,
        )
        for index, study in enumerate(review.studies, start=1)
    }
    decision_by_index, duplicate_count, invalid_count = _normalize_decisions(
        screening_decisions,
        max_study_index=len(review.studies),
    )

    tp = fp = tn = fn = 0
    for study_index, gold_label in gold_by_index.items():
        predicted_label = decision_by_index.get(study_index, "EXCLUDE")
        if gold_label == "INCLUDE":
            if predicted_label == "INCLUDE":
                tp += 1
            else:
                fn += 1
        else:
            if predicted_label == "INCLUDE":
                fp += 1
            else:
                tn += 1

    total = len(review.studies)
    gold_pass_count = sum(1 for label in gold_by_index.values() if label == "INCLUDE")
    predicted_pass_count = sum(1 for label in decision_by_index.values() if label == "INCLUDE")
    unique_decision_count = len(decision_by_index)
    missing_decision_count = total - unique_decision_count

    precision = _safe_divide(tp, tp + fp)
    recall = _safe_divide(tp, tp + fn)
    specificity = _safe_divide(tn, tn + fp)
    accuracy = _safe_divide(tp + tn, total)
    if precision is None or recall is None or precision + recall == 0:
        f1 = None
    else:
        f1 = 2 * precision * recall / (precision + recall)

    return {
        "gold_label_policy": validated_policy,
        "gold_label_policy_description": describe_screening_label_policy(validated_policy),
        "n_studies": total,
        "gold_pass_count": gold_pass_count,
        "gold_exclude_count": total - gold_pass_count,
        "predicted_pass_count": predicted_pass_count,
        "predicted_exclude_count": total - predicted_pass_count,
        "screening_decision_count": unique_decision_count,
        "missing_decision_count": missing_decision_count,
        "duplicate_decision_count": duplicate_count,
        "invalid_decision_count": invalid_count,
        "decision_coverage": _safe_divide(unique_decision_count, total),
        "parse_success": (
            total > 0
            and unique_decision_count == total
            and duplicate_count == 0
            and invalid_count == 0
        ),
        "tp": tp,
        "fp": fp,
        "tn": tn,
        "fn": fn,
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "specificity": specificity,
        "f1": f1,
    }
