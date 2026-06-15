"""Read and write ``search_metadata.json`` for a Bastirr run."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

SEARCH_METADATA_FILENAME = "search_metadata.json"
DEFAULT_INFORMATION_SOURCES = ["Cochrane benchmark dataset"]


def metadata_path(output_dir: str | Path) -> Path:
    return Path(output_dir) / SEARCH_METADATA_FILENAME


def load_search_metadata(output_dir: str | Path) -> dict[str, Any]:
    """Load search metadata from ``search_metadata.json``."""
    path = metadata_path(output_dir)
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except (json.JSONDecodeError, OSError):
        return {}


def save_search_metadata_file(output_dir: str | Path, metadata: dict[str, Any]) -> None:
    path = metadata_path(output_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def init_search_metadata(
    output_dir: str | Path,
    *,
    title: str,
    objective: str,
    background: str,
    selection_criteria: str,
) -> None:
    """Create or update protocol fields in ``search_metadata.json``."""
    metadata = load_search_metadata(output_dir)
    metadata.update({
        "title": title,
        "objective": objective,
        "background": background,
        "selection_criteria": selection_criteria,
    })
    metadata.setdefault("information_sources", DEFAULT_INFORMATION_SOURCES)
    save_search_metadata_file(output_dir, metadata)


def update_search_strategy(
    output_dir: str | Path,
    *,
    description: str | None = None,
    boolean_query: str | None = None,
    n_candidates: int | None = None,
) -> None:
    """Merge search strategy fields into ``search_metadata.json``."""
    metadata = load_search_metadata(output_dir)
    search = metadata.get("search_strategy")
    if not isinstance(search, dict):
        search = {}

    if description is not None:
        search["description"] = description.strip()
    if boolean_query is not None:
        search["boolean_query"] = boolean_query.strip()
    if n_candidates is not None:
        search["n_candidates"] = int(n_candidates)
        metadata["num_candidates"] = int(n_candidates)

    metadata["search_strategy"] = search
    metadata.setdefault("information_sources", DEFAULT_INFORMATION_SOURCES)
    save_search_metadata_file(output_dir, metadata)


def finalize_search_metadata(
    output_dir: str | Path,
    *,
    title: str,
    objective: str,
    background: str,
    selection_criteria: str,
    num_candidates: int,
) -> Path:
    """Ensure protocol and candidate counts are present; return metadata path."""
    metadata = load_search_metadata(output_dir)
    metadata.update({
        "title": title,
        "objective": objective,
        "background": background,
        "selection_criteria": selection_criteria,
        "num_candidates": int(num_candidates),
    })
    metadata.setdefault("information_sources", DEFAULT_INFORMATION_SOURCES)

    search = metadata.get("search_strategy")
    if isinstance(search, dict) and search.get("n_candidates") is None:
        search["n_candidates"] = int(num_candidates)

    save_search_metadata_file(output_dir, metadata)
    return metadata_path(output_dir)
