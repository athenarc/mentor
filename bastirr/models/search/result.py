from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional


@dataclass
class StudyRow:
    """Single study row returned from a search backend."""

    study_index: int
    title: str
    abstract: str

    # Optional fields
    doi: Optional[str] = None
    year: Optional[int] = None


@dataclass
class SearchMeta:
    """Metadata about a search query and its result set."""

    source: str
    query: str
    total_count: int
    page: int
    page_size: int
    # Extra backend-specific information (e.g. ordering, years, raw fields)
    extra: Optional[Dict[str, Any]] = None


@dataclass
class SearchResult:
    """Normalized container for search results from any backend."""

    meta: SearchMeta
    rows: List[StudyRow]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "meta": asdict(self.meta),
            "rows": [asdict(r) for r in self.rows],
        }
