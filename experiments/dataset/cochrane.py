"""
Cochrane CSV dataset paths, column map, and label semantics.

Used by ``experiments.dataset.loaders.cochrane_csv`` and screening metrics that
interpret gold labels.
"""

from __future__ import annotations

from experiments.paths import DATASET_DIR

DATASET_FILES = {
    "dev": DATASET_DIR / "20240827_dev_set.csv",
    "val": DATASET_DIR / "20240827_val_set.csv",
    "random_test": DATASET_DIR / "20240827_random_test_set.csv",
    "heart_test": DATASET_DIR / "20240827_heart_test_set.csv",
    "HIV_test": DATASET_DIR / "20240827_HIV_test_set.csv",
}

DATASET_COLUMNS = {
    "review_url": "Review_URL",
    "review_title": "Review_Title",
    "background": "Background",
    "objective": "Objective",
    "selection_criteria": "Selection_criteria",
    "study_title": "Title",
    "abstract": "Abstract_clean",
    "label": "label",
}

# 1.0 = included, 0.5 = excluded after full-text, 0.0 = excluded at screening
LABEL_INCLUDED = 1.0
LABEL_EXCLUDED_FULLTEXT = 0.5
LABEL_EXCLUDED_SCREENING = 0.0
