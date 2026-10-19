"""Loader protocol for dataset sources (Cochrane today; others later)."""

from __future__ import annotations

from typing import Optional, Protocol

from mentor.dataset.models import SystematicReview


class ReviewDatasetLoader(Protocol):
    """Common interface every dataset source should implement."""

    def load_review(
        self,
        review_url: str,
        dataset_split: str,
    ) -> Optional[SystematicReview]:
        """Load one review by source-specific id (e.g. Cochrane Review_URL)."""

    def list_reviews(self, dataset_split: str) -> list[dict]:
        """List reviews in a split with summary stats."""
