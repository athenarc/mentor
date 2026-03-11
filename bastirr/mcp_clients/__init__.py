"""
MCP clients for remote paper search and other services.

- BIP MCP and other search MCP clients live under the `search` subpackage.
- Additional MCP endpoints (PubMed, Scopus, etc.) should be added there.
"""

from bastirr.mcp_clients.search import create_bip_mcp_tool

__all__ = [
    "create_bip_mcp_tool",
]
