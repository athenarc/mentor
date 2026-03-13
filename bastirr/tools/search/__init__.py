"""
Search-related tools and clients for the Librarian agent.

This package groups together:
- local dataset search tools (Cochrane scaffolding)
- MCP-based search clients (e.g. BIP paper_search)
"""

from .search_tools import (  # noqa: F401
    get_candidates_json,
    get_review_protocol,
    load_review_data,
    search_studies,
    set_librarian_candidates,
)
from .mcp.bip_mcp_client import create_bip_mcp_tool  # noqa: F401

__all__ = [
    "load_review_data",
    "search_studies",
    "get_review_protocol",
    "set_librarian_candidates",
    "get_candidates_json",
    "create_bip_mcp_tool",
]

