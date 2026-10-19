"""Typed wrappers for MCP search tool JSON payloads.

Parses and validates dict or text responses from BIP ``paper_search`` and
PubMed search/fetch tools before mappers turn them into domain models.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
from typing import Any


@dataclass
class BipSearchResponse:
    meta: dict[str, Any]
    rows: list[dict[str, Any]]

    @classmethod
    def from_payload(cls, payload: Any) -> "BipSearchResponse":
        if not isinstance(payload, dict):
            raise ValueError("BIP paper_search payload must be a dict")
        meta = payload.get("meta")
        rows = payload.get("rows")
        if not isinstance(meta, dict):
            raise ValueError("BIP paper_search payload missing dict field 'meta'")
        if not isinstance(rows, list):
            raise ValueError("BIP paper_search payload missing list field 'rows'")
        normalized_rows = [r for r in rows if isinstance(r, dict)]
        return cls(meta=meta, rows=normalized_rows)

    @classmethod
    def from_text(cls, text: str) -> "BipSearchResponse":
        try:
            payload = json.loads(text)
        except Exception as e:  # noqa: BLE001
            raise ValueError(f"BIP paper_search text is not valid JSON: {e}") from e
        return cls.from_payload(payload)


@dataclass
class PubmedSearchResponse:
    query: str
    total_found: int | None
    offset: int | None
    pmids: list[str]

    @classmethod
    def from_payload(cls, payload: Any) -> "PubmedSearchResponse":
        if not isinstance(payload, dict):
            raise ValueError("pubmed_search_articles payload must be a dict")
        pmids_raw = payload.get("pmids")
        if not isinstance(pmids_raw, list):
            raise ValueError("pubmed_search_articles payload missing list field 'pmids'")
        pmids: list[str] = []
        for p in pmids_raw:
            v = str(p).strip()
            if v and v.isdigit():
                pmids.append(v)
        pmids = list(dict.fromkeys(pmids))

        total_raw = payload.get("totalFound")
        total_found = (
            int(total_raw) if isinstance(total_raw, (int, str)) and str(total_raw).isdigit() else None
        )
        offset_raw = payload.get("offset")
        offset = (
            int(offset_raw)
            if isinstance(offset_raw, (int, str)) and str(offset_raw).isdigit()
            else None
        )
        return cls(
            query=str(payload.get("query") or ""),
            total_found=total_found,
            offset=offset,
            pmids=pmids,
        )

@dataclass
class PubmedFetchResponse:
    articles: list[dict[str, Any]]
    total_returned: int | None

    @classmethod
    def from_payload(cls, payload: Any) -> "PubmedFetchResponse":
        if not isinstance(payload, dict):
            raise ValueError("pubmed_fetch_articles payload must be a dict")
        articles_raw = payload.get("articles")
        if not isinstance(articles_raw, list):
            raise ValueError("pubmed_fetch_articles payload missing list field 'articles'")
        total_raw = payload.get("totalReturned")
        total_returned = (
            int(total_raw) if isinstance(total_raw, (int, str)) and str(total_raw).isdigit() else None
        )
        articles = [a for a in articles_raw if isinstance(a, dict)]
        return cls(articles=articles, total_returned=total_returned)

