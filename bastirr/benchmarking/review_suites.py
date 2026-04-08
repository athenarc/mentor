"""File-backed review suite registry for the Gatekeeper screening benchmark."""

from __future__ import annotations

import json
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path


_CONFIG_PATH = Path(__file__).resolve().parent / "config" / "review_suites.json"


@dataclass(frozen=True)
class ScreeningBenchmarkReview:
    """A single review configuration in a benchmark suite."""

    key: str
    split: str
    review_url: str
    title: str
    expected_n_studies: int
    expected_n_screen_pass: int
    expected_n_screen_exclude: int


@lru_cache(maxsize=1)
def _load_review_suite_config() -> dict:
    with open(_CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


@lru_cache(maxsize=1)
def _build_canonical_review_suites() -> dict[str, tuple[ScreeningBenchmarkReview, ...]]:
    config = _load_review_suite_config()
    suites: dict[str, tuple[ScreeningBenchmarkReview, ...]] = {}
    for suite in config["canonical_suites"]:
        reviews = tuple(
            ScreeningBenchmarkReview(
                key=item["key"],
                split=item["split"],
                review_url=item["review_url"],
                title=item["title"],
                expected_n_studies=item["expected_n_studies"],
                expected_n_screen_pass=item["expected_n_screen_pass"],
                expected_n_screen_exclude=item["expected_n_screen_exclude"],
            )
            for item in suite["reviews"]
        )
        suites[suite["name"]] = reviews
    return suites


@lru_cache(maxsize=1)
def _build_review_suite_aliases() -> dict[str, str]:
    return dict(_load_review_suite_config().get("aliases", {}))


def list_review_suites() -> list[str]:
    """Return the available canonical benchmark suite names."""
    return sorted(_build_canonical_review_suites())


def get_review_suite(name: str = "screening_ladder") -> list[ScreeningBenchmarkReview]:
    """Return a copy of the requested review suite, resolving aliases."""
    canonical_name = _build_review_suite_aliases().get(name, name)
    suites = _build_canonical_review_suites()
    if canonical_name not in suites:
        raise ValueError(
            f"Unknown review suite '{name}'. Available suites: {', '.join(list_review_suites())}"
        )
    return list(suites[canonical_name])


def resolve_review_selection(
    suite_name: str = "screening_ladder",
    review_keys: list[str] | None = None,
) -> list[ScreeningBenchmarkReview]:
    """
    Resolve a suite and optional subset of review keys.

    Args:
        suite_name: Suite name to resolve.
        review_keys: Optional ordered subset of review keys within the suite.

    Returns:
        Ordered list of review specifications.
    """
    suite = get_review_suite(suite_name)
    if not review_keys:
        return suite

    review_by_key = {review.key: review for review in suite}
    unknown = [key for key in review_keys if key not in review_by_key]
    if unknown:
        raise ValueError(
            f"Unknown review key(s) for suite '{suite_name}': {', '.join(unknown)}"
        )
    return [review_by_key[key] for key in review_keys]


CANONICAL_REVIEW_SUITES = _build_canonical_review_suites()
REVIEW_SUITE_ALIASES = _build_review_suite_aliases()
