"""
Load Cochrane systematic-review rows from bundled CSV splits.

Each split file (see ``mentor.dataset.cochrane.DATASET_FILES``) contains one row per
candidate study; rows sharing a ``Review_URL`` form one ``SystematicReview``.
Ground-truth ``label`` values support benchmark scoring but are not passed to
agents during screening runs.
"""

from __future__ import annotations

import logging
from typing import List, Optional

import pandas as pd

from mentor.dataset.cochrane import DATASET_COLUMNS, DATASET_FILES, LABEL_INCLUDED
from mentor.dataset.models import Study, SystematicReview

logger = logging.getLogger(__name__)


class CochraneCsvLoader:
    """Review loader for the bundled Cochrane CSV dataset."""

    source_name = "cochrane"

    def load_review(
        self,
        review_url: str,
        dataset_split: str = "HIV_test",
    ) -> Optional[SystematicReview]:
        """
        Load a single systematic review by its Cochrane URL.

        Args:
            review_url: The Review_URL identifier.
            dataset_split: Which dataset split to load from (e.g. 'HIV_test', 'val').

        Returns:
            SystematicReview object or None if not found.
        """
        csv_path = DATASET_FILES.get(dataset_split)
        if csv_path is None or not csv_path.exists():
            logger.error("Dataset split '%s' not found at %s", dataset_split, csv_path)
            return None

        cols = DATASET_COLUMNS
        df = pd.read_csv(csv_path)

        subset = df[df[cols["review_url"]] == review_url]
        if subset.empty:
            logger.error("Review '%s' not found in %s", review_url, dataset_split)
            return None

        first = subset.iloc[0]
        review = SystematicReview(
            review_url=review_url,
            title=str(first[cols["review_title"]]),
            background=str(first[cols["background"]]),
            objective=str(first[cols["objective"]]),
            selection_criteria=str(first[cols["selection_criteria"]]),
        )

        for _, row in subset.iterrows():
            review.studies.append(
                Study(
                    title=str(row[cols["study_title"]]),
                    abstract=str(row[cols["abstract"]]),
                    label=float(row[cols["label"]]),
                )
            )

        logger.info("Loaded review: %s (%d studies)", review.title, len(review.studies))
        return review

    def list_reviews(self, dataset_split: str = "HIV_test") -> List[dict]:
        """
        List all reviews in a dataset split with summary stats.

        Returns list of dicts with keys: review_url, title, n_studies, n_included.
        """
        csv_path = DATASET_FILES.get(dataset_split)
        if csv_path is None or not csv_path.exists():
            return []

        cols = DATASET_COLUMNS
        df = pd.read_csv(csv_path)

        results = []
        for url, group in df.groupby(cols["review_url"]):
            results.append(
                {
                    "review_url": url,
                    "title": group[cols["review_title"]].iloc[0],
                    "n_studies": len(group),
                    "n_included": int((group[cols["label"]] == LABEL_INCLUDED).sum()),
                }
            )

        return sorted(results, key=lambda x: x["n_studies"])


# Default singleton used by the registry and package-level helpers.
cochrane_loader = CochraneCsvLoader()
