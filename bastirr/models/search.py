from __future__ import annotations

import json
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

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SearchResult":
        meta_raw = data.get("meta", {})
        rows_raw = data.get("rows", []) or []

        # Pull out known meta fields; everything else goes into extra.
        known_meta_keys = {"source", "query", "total_count", "page", "page_size"}
        meta_kwargs: Dict[str, Any] = {k: meta_raw.get(k) for k in known_meta_keys}

        # Provide safe defaults if some fields are missing.
        meta = SearchMeta(
            source=str(meta_kwargs.get("source") or "unknown"),
            query=str(meta_kwargs.get("query") or ""),
            total_count=int(meta_kwargs.get("total_count") or len(rows_raw)),
            page=int(meta_kwargs.get("page") or 1),
            page_size=int(meta_kwargs.get("page_size") or len(rows_raw)),
            extra={k: v for k, v in meta_raw.items() if k not in known_meta_keys} or None,
        )

        rows: List[StudyRow] = []
        for i, row in enumerate(rows_raw):
            if not isinstance(row, dict):
                continue
            title = row.get("title", "No title")
            abstract = row.get("abstract", "No abstract")
            doi = row.get("doi")
            year = row.get("year")
            # Prefer explicit index if present, otherwise use 1-based position.
            study_index = int(row.get("study_index", i + 1))
            rows.append(
                StudyRow(
                    study_index=study_index,
                    title=title,
                    abstract=abstract,
                    doi=doi,
                    year=year,
                )
            )

        return cls(meta=meta, rows=rows)

    @classmethod
    def from_json_str(cls, payload: str) -> "SearchResult":
        data = json.loads(payload)
        if not isinstance(data, dict):
            raise ValueError("SearchResult JSON must decode to an object")
        return cls.from_dict(data)

