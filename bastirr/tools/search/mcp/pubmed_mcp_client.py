"""
PubMed MCP client for remote paper search, exposed as smolagents tools.

This client connects to a PubMed MCP server via Streamable HTTP and calls
native PubMed tools:
- pubmed_search_articles
- pubmed_fetch_articles

The final response is normalized into a dict with the same
{"meta": ..., "rows": [...]} shape used by local and BIP search tools.
"""

import asyncio
import logging
from datetime import timedelta
from typing import Any

import httpx

from bastirr.models.search import (
    PubmedFetchResponse,
    PubmedSearchResponse,
    map_pubmed_response_to_result,
)

logger = logging.getLogger("bastirr.tools.search.mcp.pubmed_mcp_client")

PUBMED_SEARCH_TOOL = "pubmed_search_articles"
PUBMED_FETCH_TOOL = "pubmed_fetch_articles"

DEFAULT_TIMEOUT_SECONDS = 30.0
DEFAULT_READ_TIMEOUT_SECONDS = 300.0
INITIAL_FETCH_BATCH_SIZE = 5


def _parse_search_payload(payload: Any) -> tuple[list[str], int | None]:
    """Parse canonical pubmed_search_articles payload."""
    response = PubmedSearchResponse.from_payload(payload)
    return response.pmids, response.total_found


def _result_object_dump(result: Any) -> Any:
    """Best-effort dump of the full call_tool result object."""
    try:
        if hasattr(result, "model_dump"):
            return result.model_dump()
    except Exception:  # noqa: BLE001
        pass
    try:
        if hasattr(result, "dict"):
            return result.dict()
    except Exception:  # noqa: BLE001
        pass
    return repr(result)


def _extract_structured_content(result: Any) -> Any:
    """Read structured payload from SDK object or raw dumped object.

    Keep strict behavior: only structured content is accepted.
    """
    if hasattr(result, "structured_content"):
        structured = getattr(result, "structured_content")
        if structured is not None:
            return structured
    dumped = _result_object_dump(result)
    if isinstance(dumped, dict):
        if dumped.get("structured_content") is not None:
            return dumped.get("structured_content")
        if dumped.get("structuredContent") is not None:
            return dumped.get("structuredContent")
    return None


async def _search_and_fetch_pubmed_async(
    url: str,
    query: str,
    *,
    offset: int,
    limit: int,
    sort: str,
) -> dict:
    from mcp import ClientSession
    from mcp.client.streamable_http import streamable_http_client
    from mcp.shared._httpx_utils import create_mcp_http_client

    timeout_obj = httpx.Timeout(DEFAULT_TIMEOUT_SECONDS, read=DEFAULT_READ_TIMEOUT_SECONDS)
    async with create_mcp_http_client(timeout=timeout_obj) as client:
        async with streamable_http_client(url, http_client=client) as (
            read_stream,
            write_stream,
            _,
        ):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()

                # Canonical schema for pubmed_search_articles:
                # query (required), maxResults, offset, sort
                search_result = await session.call_tool(
                    PUBMED_SEARCH_TOOL,
                    arguments={
                        "query": query,
                        "maxResults": limit,
                        "offset": offset,
                        "sort": sort,
                    },
                    read_timeout_seconds=timedelta(seconds=DEFAULT_READ_TIMEOUT_SECONDS),
                )
                search_structured = _extract_structured_content(search_result)
                if search_structured is None:
                    raise ValueError("pubmed_search_articles returned no structured_content")
                pmids, total_found = _parse_search_payload(search_structured)
                if not pmids:
                    raise ValueError("pubmed_search_articles returned no pmids")

                # Fetch details in adaptive chunks to avoid server XML expansion limits.
                all_articles: list[dict[str, Any]] = []
                i = 0
                batch_size = INITIAL_FETCH_BATCH_SIZE
                while i < len(pmids):
                    chunk = pmids[i : i + batch_size]
                    fetch_arguments = {
                        "pmids": chunk,
                        "includeMesh": True,
                        "includeGrants": False,
                    }
                    try:
                        fetch_result = await session.call_tool(
                            PUBMED_FETCH_TOOL,
                            arguments=fetch_arguments,
                            read_timeout_seconds=timedelta(seconds=DEFAULT_READ_TIMEOUT_SECONDS),
                        )
                        fetch_structured = _extract_structured_content(fetch_result)
                        if fetch_structured is None:
                            raise ValueError("pubmed_fetch_articles returned no structured_content")
                        chunk_response = PubmedFetchResponse.from_payload(fetch_structured)
                        all_articles.extend(chunk_response.articles)
                        i += len(chunk)
                        # Reset to preferred size after successful retries.
                        batch_size = INITIAL_FETCH_BATCH_SIZE
                    except Exception as e:  # noqa: BLE001
                        logger.warning(
                            "PubMed fetch failed for batch of %d PMIDs; query=%r; error=%s",
                            len(chunk),
                            query,
                            e,
                        )
                        print(
                            "PubMed fetch retry: "
                            f"query={query!r}, failed_batch_size={len(chunk)}, error={e}"
                        )
                        if len(chunk) == 1:
                            raise ValueError(
                                f"pubmed_fetch_articles failed for PMID {chunk[0]}: {e}"
                            ) from e
                        batch_size = max(1, len(chunk) // 2)

    fetch_response = PubmedFetchResponse(
        articles=all_articles,
        total_returned=len(all_articles),
    )
    result = map_pubmed_response_to_result(
        response=fetch_response,
        query=query,
        offset=offset,
        limit=limit,
        sort=sort,
        pmids_found=len(pmids),
        search_total_found=total_found,
    )
    return result.to_dict()


def search_pubmed(
    url: str,
    query: str,
    *,
    offset: int = 0,
    limit: int = 20,
    sort: str = "relevance",
) -> dict:
    """Search PubMed MCP and return normalized rows."""
    try:
        return asyncio.run(
            _search_and_fetch_pubmed_async(
                url=url,
                query=query,
                offset=offset,
                limit=limit,
                sort=sort,
            )
        )
    except Exception as e:  # noqa: BLE001
        logger.exception("PubMed MCP search failed")
        return {"error": True, "message": str(e)}


def create_pubmed_mcp_tool(pubmed_mcp_url: str):
    """Create a smolagents tool for PubMed MCP search."""
    from smolagents import tool

    @tool
    def search_papers_in_pubmed(
        query: str,
        offset: int = 0,
        limit: int = 20,
        sort: str = "relevance",
    ) -> dict:
        """
        Search for research papers via the PubMed MCP server.

        This tool calls native PubMed MCP search/fetch tools and returns a
        normalized dict:
          {"meta": {...}, "rows": [{title, abstract, doi, year, ...}, ...]}

        Args:
            query: PubMed query string.
            offset: Pagination offset (0-based).
            limit: Maximum records to retrieve.
            sort: Sort option passed to PubMed MCP search.

        Returns:
            A Python dict with normalized rows or an error dict.
        """
        return search_pubmed(
            url=pubmed_mcp_url,
            query=query,
            offset=offset,
            limit=limit,
            sort=sort,
        )

    return search_papers_in_pubmed
