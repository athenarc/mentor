"""
Benchmark review suites and suite runner for Mentor.

Suites are defined in ``experiments/config/suites.json``. Each suite lists reviews
and an optional ``run`` block (``profiles`` list, repeats, batch_size, stages).
Runs reference profiles only; models are leaf connections inside profiles.
"""

from experiments.suites.review_suites import (
    ScreeningBenchmarkReview,
    SuiteRunConfig,
    expand_suite_run_config,
    get_review_suite,
    list_review_suites,
    resolve_review_selection,
)

__all__ = [
    "ScreeningBenchmarkReview",
    "SuiteRunConfig",
    "expand_suite_run_config",
    "get_review_suite",
    "list_review_suites",
    "resolve_review_selection",
]
