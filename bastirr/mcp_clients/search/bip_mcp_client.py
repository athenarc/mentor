"""
BIP MCP client for remote paper search.

Connects to the BIP MCP server (https://bip-mcp.imsi.athenarc.gr/mcp)
via Streamable HTTP and calls the paper_search tool. Used by the Librarian
as an additional search backend alongside the pre-loaded dataset.
"""

import asyncio
import json
import logging
from typing import Any

from datetime import timedelta

import httpx

logger = logging.getLogger("bastirr.mcp_clients.search.bip_mcp_client")

# Tool name on the BIP MCP server
SEARCH_PAPERS_TOOL = "paper_search"

# ---------------------------------------------------------------------------
# Timeout configuration for BIP MCP client
# ---------------------------------------------------------------------------
# General HTTP timeout (seconds) for connect/write operations
DEFAULT_TIMEOUT_SECONDS = 30.0
# Read timeout (seconds) for streaming responses
DEFAULT_READ_TIMEOUT_SECONDS = 300.0


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
) -> str:
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
        Response text from the tool (JSON or formatted string). On connection
        or tool error, returns a JSON object with an "error" key.
    """
    from mcp import ClientSession
    from mcp.client.streamable_http import streamable_http_client
    from mcp.shared._httpx_utils import create_mcp_http_client

    async def _run() -> str:
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

        headers: dict[str, str] | None = None
        if auth_token:
            value = (
                auth_token
                if auth_token.strip().lower().startswith("bearer ")
                else f"Bearer {auth_token}"
            )
            headers = {"Authorization": value}

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
                        read_timeout_seconds=timedelta(
                            seconds=DEFAULT_READ_TIMEOUT_SECONDS
                        ),
                    )

        # Build response text from the CallToolResult; if the server
        # returned an MCP error, the client will typically raise before
        # this point. We keep this simple and let exceptions propagate.
        parts: list[str] = []
        if hasattr(result, "content") and result.content:
            for block in result.content:
                if hasattr(block, "text") and block.text:
                    parts.append(block.text)
        if hasattr(result, "structured_content") and result.structured_content is not None:
            parts.append(
                json.dumps(result.structured_content, ensure_ascii=False, indent=2)
            )
        if not parts:
            msg = json.dumps({"message": "No content returned from paper_search"})
            logger.info("BIP MCP paper_search query=%r returned no content.", keywords)
            return msg

        text = "\n\n".join(parts)
        return text

    try:
        return asyncio.run(_run())
    except Exception as e:  # noqa: BLE001
        logger.exception("BIP MCP paper_search failed")
        return json.dumps({"error": True, "message": str(e)})


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
    ) -> str:
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
            JSON or text response from the paper search. On error, a JSON object
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

