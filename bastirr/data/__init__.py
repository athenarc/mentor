"""
Data loader for Cochrane systematic review dataset.

Loads a single review with all its candidate studies, structured
for consumption by the Bastirr agent pipeline.
"""

import logging
from dataclasses import dataclass, field
from typing import List, Optional

import pandas as pd

from bastirr.config import DATASET_FILES, DATASET_COLUMNS, LABEL_INCLUDED

logger = logging.getLogger(__name__)


@dataclass
class Study:
    """A single candidate study (title + abstract + ground-truth label)."""
    title: str
    abstract: str
    label: float  # 1.0 included, 0.5 excluded full-text, 0.0 excluded screening

    @property
    def is_included(self) -> bool:
        return self.label == LABEL_INCLUDED


@dataclass
class SystematicReview:
    """A complete systematic review with its protocol and candidate studies."""
    review_url: str
    title: str
    background: str
    objective: str
    selection_criteria: str
    studies: List[Study] = field(default_factory=list)

    @property
    def included_studies(self) -> List[Study]:
        return [s for s in self.studies if s.is_included]

    @property
    def excluded_studies(self) -> List[Study]:
        return [s for s in self.studies if not s.is_included]

    def summary(self) -> str:
        return (
            f"Review: {self.title}\n"
            f"  Studies: {len(self.studies)} total, "
            f"{len(self.included_studies)} included, "
            f"{len(self.excluded_studies)} excluded\n"
            f"  Objective: {self.objective[:150]}..."
        )


def load_review(
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
        logger.error(f"Dataset split '{dataset_split}' not found at {csv_path}")
        return None

    cols = DATASET_COLUMNS
    df = pd.read_csv(csv_path)

    subset = df[df[cols["review_url"]] == review_url]
    if subset.empty:
        logger.error(f"Review '{review_url}' not found in {dataset_split}")
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

    logger.info(f"Loaded review: {review.title} ({len(review.studies)} studies)")
    return review


def list_reviews(dataset_split: str = "HIV_test") -> List[dict]:
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
        results.append({
            "review_url": url,
            "title": group[cols["review_title"]].iloc[0],
            "n_studies": len(group),
            "n_included": int((group[cols["label"]] == LABEL_INCLUDED).sum()),
        })

    return sorted(results, key=lambda x: x["n_studies"])
