"""
MCP-based search clients used by the Librarian.

Currently includes:
- BIP MCP paper_search client
- PubMed MCP search/fetch client
"""

from .bip_mcp_client import create_bip_mcp_tool  # noqa: F401
from .pubmed_mcp_client import create_pubmed_mcp_tool  # noqa: F401

__all__ = [
    "create_bip_mcp_tool",
    "create_pubmed_mcp_tool",
]

