"""
Dataset access for Mentor: shared review models + pluggable source loaders.

Domain types live in ``models``. Concrete sources live in ``loaders/``
(e.g. ``loaders/cochrane_csv.py``). Use ``load_review`` / ``list_reviews``
here, or ``get_loader(source)`` from ``registry`` when adding a new source.
"""

from __future__ import annotations

from mentor.dataset.models import Study, SystematicReview
from mentor.dataset.registry import (
    DEFAULT_SOURCE,
    get_loader,
    list_sources,
    register_loader,
)

__all__ = [
    "Study",
    "SystematicReview",
    "DEFAULT_SOURCE",
    "get_loader",
    "list_sources",
    "register_loader",
    "load_review",
    "list_reviews",
]


def load_review(
    review_url: str,
    dataset_split: str = "HIV_test",
    *,
    source: str = DEFAULT_SOURCE,
):
    """Load a review via the registered ``source`` loader (default: Cochrane)."""
    return get_loader(source).load_review(review_url, dataset_split)


def list_reviews(
    dataset_split: str = "HIV_test",
    *,
    source: str = DEFAULT_SOURCE,
):
    """List reviews via the registered ``source`` loader (default: Cochrane)."""
    return get_loader(source).list_reviews(dataset_split)
