"""
MCP-based search clients used by the Librarian.

Currently includes:
- BIP MCP paper_search client
"""

from .bip_mcp_client import create_bip_mcp_tool  # noqa: F401

__all__ = [
    "create_bip_mcp_tool",
]

