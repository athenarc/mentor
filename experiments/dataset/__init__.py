"""
Cochrane (and future) dataset loaders for experiments.

Gold labels stay here for ``experiments analyze``. Mentor never imports this
package; suite cells materialize unlabeled ``review.json`` for Mentor.
"""

from __future__ import annotations

from experiments.dataset.models import Study, SystematicReview
from experiments.dataset.registry import (
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
