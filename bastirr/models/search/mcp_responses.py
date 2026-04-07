from __future__ import annotations

from dataclasses import dataclass
import json
import re
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

    @classmethod
    def from_text(cls, text: str) -> "PubmedSearchResponse":
        # Expected format includes:
        # **Query:** ...
        # **Total Found:** N | **Returned:** ...
        # **PMIDs:** 1, 2, 3
        q_match = re.search(r"\*\*Query:\*\*\s*(.+)", text)
        query = q_match.group(1).strip() if q_match else ""

        tf_match = re.search(r"\*\*Total Found:\*\*\s*(\d+)", text)
        total_found = int(tf_match.group(1)) if tf_match else None

        off_match = re.search(r"\*\*Offset:\*\*\s*(\d+)", text)
        offset = int(off_match.group(1)) if off_match else None

        pmids: list[str] = []
        pmids_match = re.search(r"\*\*PMIDs:\*\*\s*([0-9,\s]+)", text)
        if pmids_match:
            raw = pmids_match.group(1)
            for part in raw.split(","):
                p = part.strip()
                if p.isdigit():
                    pmids.append(p)
        pmids = list(dict.fromkeys(pmids))
        if not pmids:
            raise ValueError("pubmed_search_articles text response missing PMID list")
        return cls(query=query, total_found=total_found, offset=offset, pmids=pmids)


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

    @classmethod
    def from_text(cls, text: str) -> "PubmedFetchResponse":
        # Expected markdown-style blocks:
        # ## PubMed Articles
        # **Articles Returned:** N
        # ### <title>
        # ... **PMID:** ... **DOI:** ... **Journal:** ..., YYYY, ...
        total_match = re.search(r"\*\*Articles Returned:\*\*\s*(\d+)", text)
        total_returned = int(total_match.group(1)) if total_match else None

        parts = re.split(r"\n###\s+", text)
        articles: list[dict[str, Any]] = []
        for part in parts[1:]:
            block = part.strip()
            if not block:
                continue
            title = block.split("\n", 1)[0].strip()
            pmid_match = re.search(r"\*\*PMID:\*\*\s*(\d+)", block)
            doi_match = re.search(r"\*\*DOI:\*\*\s*([^\s]+)", block)
            year_match = re.search(r",\s*(\d{4})\s*,", block)
            articles.append(
                {
                    "title": title,
                    "abstract": "",
                    "pmid": pmid_match.group(1) if pmid_match else None,
                    "doi": doi_match.group(1) if doi_match else None,
                    "year": int(year_match.group(1)) if year_match else None,
                }
            )

        if not articles:
            raise ValueError("pubmed_fetch_articles text response missing article blocks")
        return cls(articles=articles, total_returned=total_returned)
