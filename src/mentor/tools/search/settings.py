"""
Librarian search-source toggles and MCP endpoint settings.

Controlled by ``SEARCH_SOURCES`` (comma-separated: ``local``, ``bip``, ``pubmed``)
plus BIP / PubMed MCP URL and auth env vars.
"""

from __future__ import annotations

import os

import mentor.settings  # noqa: F401  # load .env before reading SEARCH_* vars

_SEARCH_SOURCE_TOKENS = {
    t.strip().lower()
    for t in os.getenv("SEARCH_SOURCES", "local").split(",")
    if t.strip()
}
_VALID_SEARCH_SOURCES = {"local", "bip", "pubmed"}
_INVALID_SEARCH_SOURCES = sorted(_SEARCH_SOURCE_TOKENS - _VALID_SEARCH_SOURCES)
if _INVALID_SEARCH_SOURCES:
    raise ValueError(
        "Invalid SEARCH_SOURCES value(s): "
        f"{', '.join(_INVALID_SEARCH_SOURCES)}. "
        "Allowed values: local, bip, pubmed."
    )
SEARCH_SOURCES = _SEARCH_SOURCE_TOKENS

BIP_MCP_URL = os.getenv("SEARCH_BIP_MCP_URL", "")
BIP_MCP_AUTH_TOKEN = os.getenv("SEARCH_BIP_AUTH_TOKEN", "")
PUBMED_MCP_URL = os.getenv("SEARCH_PUBMED_MCP_URL", "")
