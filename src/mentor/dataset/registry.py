"""Registry of dataset sources. Add new modules under ``dataset/loaders/``."""

from __future__ import annotations

from mentor.dataset.base import ReviewDatasetLoader
from mentor.dataset.loaders.cochrane_csv import cochrane_loader

DEFAULT_SOURCE = "cochrane"

_LOADERS: dict[str, ReviewDatasetLoader] = {
    cochrane_loader.source_name: cochrane_loader,
}


def list_sources() -> list[str]:
    """Return registered dataset source names."""
    return sorted(_LOADERS)


def get_loader(source: str = DEFAULT_SOURCE) -> ReviewDatasetLoader:
    """Return the loader for ``source`` (default: Cochrane CSV)."""
    try:
        return _LOADERS[source]
    except KeyError as exc:
        available = ", ".join(list_sources()) or "(none)"
        raise ValueError(
            f"Unknown dataset source '{source}'. Available: {available}"
        ) from exc


def register_loader(name: str, loader: ReviewDatasetLoader) -> None:
    """Register or replace a dataset loader (useful for tests / plugins)."""
    _LOADERS[name] = loader
