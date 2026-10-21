"""
Gatekeeper screening analysis harness — metrics, suites, and scoring artifacts.

Execution lives in ``experiments.suites.runner`` (``experiments suite``).
Post-run scoring is in ``experiments.harness.analysis``.
"""

from experiments.harness.analysis import analyze_experiment
from experiments.harness.inspection import (
    build_screening_inspection_payload,
    gold_label_to_review_outcome,
    write_screening_inspection_artifacts,
)
from experiments.harness.metrics import (
    SCREENING_LABEL_POLICIES,
    compute_screening_metrics,
    describe_screening_label_policy,
    gold_label_to_screening_decision,
    gold_screening_policy_mapping,
    validate_screening_label_policy,
)
from experiments.catalog import list_models, resolve_model
from experiments.suites.review_suites import (
    get_review_suite,
    list_review_suites,
    resolve_review_selection,
)

__all__ = [
    "analyze_experiment",
    "build_screening_inspection_payload",
    "describe_screening_label_policy",
    "compute_screening_metrics",
    "gold_label_to_screening_decision",
    "gold_screening_policy_mapping",
    "gold_label_to_review_outcome",
    "get_review_suite",
    "list_models",
    "list_review_suites",
    "resolve_model",
    "resolve_review_selection",
    "SCREENING_LABEL_POLICIES",
    "validate_screening_label_policy",
    "write_screening_inspection_artifacts",
]
