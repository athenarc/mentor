"""
Domain models package.

Currently contains search-related models in ``bastirr.models.search`` package.
"""

from .search import (
    BipSearchResponse,
    PubmedFetchResponse,
    PubmedSearchResponse,
    SearchMeta,
    SearchResult,
    StudyRow,
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

