"""
Search domain models and mapping utilities.
"""

from .mcp_responses import BipSearchResponse, PubmedFetchResponse, PubmedSearchResponse
from .result import SearchMeta, SearchResult, StudyRow
from .mappers import (
    map_bip_response_to_result,
    map_local_studies_to_result,
    map_pubmed_response_to_result,
)

__all__ = [
    "SearchMeta",
    "SearchResult",
    "StudyRow",
    "BipSearchResponse",
    "PubmedSearchResponse",
    "PubmedFetchResponse",
    "map_local_studies_to_result",
    "map_bip_response_to_result",
    "map_pubmed_response_to_result",
]
