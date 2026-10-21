"""Map raw search backend payloads into normalized ``SearchResult`` objects.

Each mapper builds ``SearchMeta`` and ``StudyRow`` lists for local review
data, BIP MCP responses, or PubMed fetch results so agent tools share one
result shape regardless of upstream API.
"""

from __future__ import annotations

from typing import Any

from .mcp_responses import BipSearchResponse, PubmedFetchResponse
from .result import SearchMeta, SearchResult, StudyRow


def map_local_studies_to_result(query: str, studies: list[Any]) -> SearchResult:
    rows: list[StudyRow] = []
    for i, study in enumerate(studies, start=1):
        title = study.get("title", "No title") if isinstance(study, dict) else "No title"
        abstract = (
            study.get("abstract", "No abstract") if isinstance(study, dict) else "No abstract"
        )
        rows.append(StudyRow(study_index=i, title=title, abstract=abstract))

    meta = SearchMeta(
        source="local",
        query=query,
        total_count=len(rows),
        page=1,
        page_size=len(rows),
    )
    return SearchResult(meta=meta, rows=rows)


# BIP MCP paper_search JSON


def map_bip_response_to_result(response: BipSearchResponse) -> SearchResult:
    meta_raw = response.meta
    rows_raw = response.rows or []

    known_meta_keys = {"source", "query", "total_count", "page", "page_size"}
    meta_kwargs: dict[str, Any] = {k: meta_raw.get(k) for k in known_meta_keys}

    meta = SearchMeta(
        source=str(meta_kwargs.get("source") or "unknown"),
        query=str(meta_kwargs.get("query") or ""),
        total_count=int(meta_kwargs.get("total_count") or len(rows_raw)),
        page=int(meta_kwargs.get("page") or 1),
        page_size=int(meta_kwargs.get("page_size") or len(rows_raw)),
        extra={k: v for k, v in meta_raw.items() if k not in known_meta_keys} or None,
    )

    rows: list[StudyRow] = []
    for i, row in enumerate(rows_raw):
        if not isinstance(row, dict):
            continue
        title = row.get("title", "No title")
        abstract = row.get("abstract", "No abstract")
        doi = row.get("doi")
        year = row.get("year")
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
    return SearchResult(meta=meta, rows=rows)


# PubMed MCP search + fetch pipeline


def map_pubmed_response_to_result(
    *,
    response: PubmedFetchResponse,
    query: str,
    offset: int,
    limit: int,
    sort: str,
    pmids_found: int,
    search_total_found: int | None,
) -> SearchResult:
    articles = response.articles
    rows: list[StudyRow] = []
    for i, article in enumerate(articles, start=1):
        if not isinstance(article, dict):
            continue
        title = article.get("title")
        if not isinstance(title, str) or not title.strip():
            continue
        abstract = article.get("abstract") or article.get("summary") or ""
        year_raw = article.get("year") or article.get("pub_year")
        year = int(year_raw) if isinstance(year_raw, (int, str)) and str(year_raw).isdigit() else None
        doi = article.get("doi")
        rows.append(
            StudyRow(
                study_index=i,
                title=title.strip(),
                abstract=abstract.strip() if isinstance(abstract, str) else "",
                doi=doi.strip() if isinstance(doi, str) else None,
                year=year,
            )
        )
    total_returned = response.total_returned
    meta = SearchMeta(
        source="pubmed_mcp",
        query=query,
        total_count=search_total_found or total_returned or len(rows),
        page=(offset // max(limit, 1)) + 1,
        page_size=limit,
        extra={
            "offset": offset,
            "sort": sort,
            "pmids_found": pmids_found,
            "used_fetch_tool": bool(pmids_found),
            "search_total_found": search_total_found,
            "fetch_total_returned": total_returned,
        },
    )
    return SearchResult(meta=meta, rows=rows)
