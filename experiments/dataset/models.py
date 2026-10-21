"""Shared domain types for systematic reviews loaded from any dataset source."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from experiments.dataset.cochrane import LABEL_INCLUDED


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
