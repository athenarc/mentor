"""
Search-related MCP clients (e.g. BIP search).

New search MCP endpoints (PubMed, Scopus, etc.) should live in this package.
"""

from bastirr.mcp_clients.search.bip_mcp_client import create_bip_mcp_tool

__all__ = [
    "create_bip_mcp_tool",
]

