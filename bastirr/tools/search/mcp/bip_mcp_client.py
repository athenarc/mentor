"""
BIP MCP client for remote paper search, exposed as a smolagents tool.

This client connects to the BIP MCP server (https://bip-mcp.imsi.athenarc.gr/mcp)
via Streamable HTTP and calls the ``paper_search`` tool. It returns a normalized
JSON structure in the same ``{"meta": ..., "rows": [...]}`` format used by the
local ``search_studies`` tool.
"""

import asyncio
import json
import logging
from typing import Any

from datetime import timedelta

import httpx

from bastirr.models.search import SearchResult

logger = logging.getLogger("bastirr.tools.search.mcp.bip_mcp_client")

# Tool name on the BIP MCP server
SEARCH_PAPERS_TOOL = "paper_search"

# ---------------------------------------------------------------------------
# Timeout configuration for BIP MCP client
# ---------------------------------------------------------------------------
# General HTTP timeout (seconds) for connect/write operations
DEFAULT_TIMEOUT_SECONDS = 30.0
# Read timeout (seconds) for streaming responses
DEFAULT_READ_TIMEOUT_SECONDS = 300.0


def _build_arguments(
    keywords: str,
    ordering: str,
    page: int,
    page_size: int,
    start_year: int | None,
    end_year: int | None,
) -> dict[str, Any]:
    arguments: dict[str, Any] = {
        "keywords": keywords,
        "ordering": ordering,
        "page": page,
        "page_size": page_size,
    }
    if start_year is not None:
        arguments["start_year"] = start_year
    if end_year is not None:
        arguments["end_year"] = end_year
    return arguments


def _build_headers(auth_token: str | None) -> dict[str, str] | None:
    if not auth_token:
        return None
    value = (
        auth_token
        if auth_token.strip().lower().startswith("bearer ")
        else f"Bearer {auth_token}"
    )
    return {"Authorization": value}


def _normalize_structured_content(content: Any) -> dict:
    """Normalize structured_content into the common SearchResult dict schema."""
    try:
        normalized = SearchResult.from_dict(content)
    except Exception as e:  # noqa: BLE001
        logger.exception("Failed to normalize structured_content from BIP MCP: %s", e)
        # Fall back to the raw content as-is (it should already be JSON-serializable).
        return content
    return normalized.to_dict()


def _normalize_text_content(text: str, keywords: str) -> dict:
    """Normalize textual content into a dict, using SearchResult when possible.

    This first tries to parse the raw text directly into a SearchResult via
    ``SearchResult.from_json_str``. If that fails because the text is not
    valid JSON or has an unexpected structure, it falls back to a minimal
    wrapper dict so callers always receive a JSON-serializable object.
    """
    try:
        normalized = SearchResult.from_json_str(text)
    except Exception as e:  # noqa: BLE001
        logger.exception("Failed to normalize textual response from BIP MCP: %s", e)
        # Non-JSON or unexpected text; wrap into a minimal dict envelope.
        return {
            "meta": {
                "source": "bip_mcp",
                "keywords": keywords,
                "message": "Non-JSON or unexpected textual response from paper_search",
            },
            "rows_text": [text],
        }

    return normalized.to_dict()


async def _call_search_papers_async(
    url: str,
    keywords: str,
    *,
    ordering: str,
    start_year: int | None,
    end_year: int | None,
    page: int,
    page_size: int,
    auth_token: str | None,
) -> dict:
    """Internal async implementation that talks to the MCP server."""
    from mcp import ClientSession
    from mcp.client.streamable_http import streamable_http_client
    from mcp.shared._httpx_utils import create_mcp_http_client

    arguments = _build_arguments(
        keywords=keywords,
        ordering=ordering,
        page=page,
        page_size=page_size,
        start_year=start_year,
        end_year=end_year,
    )
    headers = _build_headers(auth_token)

    timeout_obj = httpx.Timeout(
        DEFAULT_TIMEOUT_SECONDS,
        read=DEFAULT_READ_TIMEOUT_SECONDS,
    )
    async with create_mcp_http_client(headers=headers, timeout=timeout_obj) as client:
        async with streamable_http_client(url, http_client=client) as (
            read_stream,
            write_stream,
            _,
        ):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()
                result = await session.call_tool(
                    SEARCH_PAPERS_TOOL,
                    arguments=arguments,
                    read_timeout_seconds=timedelta(seconds=DEFAULT_READ_TIMEOUT_SECONDS),
                )

    # Prefer structured_content and normalize it; otherwise, fall back to text.
    if hasattr(result, "structured_content") and result.structured_content is not None:
        return _normalize_structured_content(result.structured_content)

    parts: list[str] = []
    if hasattr(result, "content") and result.content:
        for block in result.content:
            if hasattr(block, "text") and block.text:
                parts.append(block.text)

    if not parts:
        logger.info("BIP MCP paper_search query=%r returned no content.", keywords)
        return {
            "meta": {
                "source": "bip_mcp",
                "keywords": keywords,
                "message": "No content returned from paper_search",
            },
            "rows": [],
        }

    text = "\n\n".join(parts)
    return _normalize_text_content(text, keywords)


def call_search_papers(
    url: str,
    keywords: str,
    *,
    ordering: str = "popularity",
    start_year: int | None = None,
    end_year: int | None = None,
    page: int = 1,
    page_size: int = 20,
    auth_token: str | None = None,
) -> dict:
    """
    Call the BIP MCP server's paper_search tool via Streamable HTTP.

    Args:
        url: BIP MCP server endpoint (e.g. https://bip-mcp.imsi.athenarc.gr/mcp).
        keywords: Search query string.
        ordering: Sort order (e.g. popularity, year, citation_count).
        start_year: Optional filter: papers after this year.
        end_year: Optional filter: papers before this year.
        page: Page number (1-based).
        page_size: Results per page.
        auth_token: Optional Bearer token (required by BIP MCP server).

    Returns:
        A Python dict. On success, this is the normalized structured result
        in the common ``{"meta": ..., "rows": [...]}`` format. On connection
        or tool error, returns a dict with an ``"error"`` key.
    """
    try:
        return asyncio.run(
            _call_search_papers_async(
                url=url,
                keywords=keywords,
                ordering=ordering,
                start_year=start_year,
                end_year=end_year,
                page=page,
                page_size=page_size,
                auth_token=auth_token,
            )
        )
    except Exception as e:  # noqa: BLE001
        logger.exception("BIP MCP paper_search failed")
        return {"error": True, "message": str(e)}


def create_bip_mcp_tool(bip_mcp_url: str, auth_token: str = ""):
    """
    Create a smolagents tool that calls the BIP MCP server's paper_search tool.

    Args:
        bip_mcp_url: BIP MCP server Streamable HTTP URL.
        auth_token: Optional Bearer token (BIP MCP server requires auth).

    Returns:
        A @tool-decorated function suitable for the Librarian agent.
    """
    from smolagents import tool

    token = auth_token or None

    @tool
    def search_papers_in_bip(
        query: str,
        page: int = 1,
        page_size: int = 20,
        ordering: str = "popularity",
        start_year: int | None = None,
        end_year: int | None = None,
    ) -> dict:
        """
        Search for research papers via the BIP MCP server (external literature database).

        Use this in addition to search_studies() to find more candidates. Results
        are returned as JSON with meta (total_count, page) and rows (title, abstract,
        doi, authors, journal, year, etc.). Requires SEARCH_BIP_AUTH_TOKEN if the server needs auth.

        Args:
            query: Search keywords or research question.
            page: Page number (1-based). Default 1.
            page_size: Number of results per page. Default 20.
            ordering: Sort by popularity, influence, citation_count, impulse, or year.
            start_year: Only papers published after this year (optional).
            end_year: Only papers published before this year (optional).

        Returns:
            A Python dict response from the paper search. On error, a dict
            with "error": true and "message" is returned.
        """
        return call_search_papers(
            url=bip_mcp_url,
            keywords=query,
            page=page,
            page_size=page_size,
            ordering=ordering,
            start_year=start_year,
            end_year=end_year,
            auth_token=token,
        )

    return search_papers_in_bip

