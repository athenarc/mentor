"""
Study store, getter tools, and external search clients for the Librarian.

Runners call ``load_review_data`` before agents start. Librarian search tools
write candidates into the shared store; orchestrators and benchmarks read them
through ``get_candidates_json`` and loop/chunk getters.

Normalized search DTOs live in ``mentor.tools.search.models``.
"""

from .search_tools import (  # noqa: F401
    get_candidate_studies_chunk_json,
    get_candidate_study_json,
    get_candidates_json,
    get_review_protocol,
    load_review_data,
    search_studies,
    set_librarian_candidates,
)
from .mcp.bip_mcp_client import create_bip_mcp_tool  # noqa: F401
from .mcp.pubmed_mcp_client import create_pubmed_mcp_tool  # noqa: F401

__all__ = [
    "load_review_data",
    "search_studies",
    "get_review_protocol",
    "set_librarian_candidates",
    "get_candidates_json",
    "get_candidate_study_json",
    "get_candidate_studies_chunk_json",
    "create_bip_mcp_tool",
    "create_pubmed_mcp_tool",
]
