"""
Canonical review suites (``experiments/config/suites.json``).

Each review entry is a Cochrane ``key`` (review URL) plus dataset ``split``.
Optional per-suite ``run`` blocks list **profiles** (not raw model keys),
plus repeats, batch_size, and mode.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

from experiments.catalog import resolve_profile_agents


_CONFIG_PATH = Path(__file__).resolve().parents[1] / "config" / "suites.json"
_DOI_SEGMENT = re.compile(
    r"(?<=^https://www\.cochranelibrary\.com/cdsr/doi/10\.1002/)[\w.]+(?=/full$)"
)


@dataclass(frozen=True)
class ScreeningBenchmarkReview:
    """A single review configuration in a benchmark suite.

    ``key`` is the Cochrane review URL used to load the dataset row.
    """

    key: str
    split: str

    @property
    def path_slug(self) -> str:
        """Filesystem-safe id derived from the Cochrane DOI in ``key``."""
        match = _DOI_SEGMENT.search(self.key)
        if match:
            return match.group(0).lower().replace(".", "_")
        return re.sub(r"[^A-Za-z0-9._-]+", "_", self.key).strip("_")


@dataclass(frozen=True)
class RoleModelMap:
    """One concrete role→model-key assignment expanded from a profile."""

    profile_key: str
    agents: dict[str, str]  # role → model catalogue key
    label: str


@dataclass(frozen=True)
class SuiteRunConfig:
    """Expanded run configuration for a suite."""

    configurations: list[RoleModelMap]
    repeats: int = 1
    batch_size: int | None = None
    mode: str = "screening-only"

    def __post_init__(self) -> None:
        if self.repeats < 1:
            raise ValueError("repeats must be at least 1")
        if self.batch_size is not None and self.batch_size < 1:
            raise ValueError("batch_size must be at least 1 when provided")
        allowed = {"full", "screening-only"}
        if self.mode not in allowed:
            raise ValueError(
                f"mode must be one of {sorted(allowed)}, got {self.mode!r}"
            )
        if not self.configurations:
            raise ValueError("Suite run config has no profile configurations.")


@lru_cache(maxsize=1)
def _load_review_suite_config() -> dict:
    with open(_CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


@lru_cache(maxsize=1)
def _build_canonical_review_suites() -> dict[str, tuple[ScreeningBenchmarkReview, ...]]:
    config = _load_review_suite_config()
    suites: dict[str, tuple[ScreeningBenchmarkReview, ...]] = {}
    for suite in config["canonical_suites"]:
        reviews = tuple(
            ScreeningBenchmarkReview(
                key=item["key"],
                split=item["split"],
            )
            for item in suite["reviews"]
        )
        suites[suite["name"]] = reviews
    return suites


@lru_cache(maxsize=1)
def _raw_suite_by_name() -> dict[str, dict[str, Any]]:
    return {suite["name"]: suite for suite in _load_review_suite_config()["canonical_suites"]}


def list_review_suites() -> list[str]:
    """Return the available canonical suite names."""
    return sorted(_build_canonical_review_suites())


def get_review_suite(name: str = "screening_ladder") -> list[ScreeningBenchmarkReview]:
    """Return a copy of the requested review suite."""
    suites = _build_canonical_review_suites()
    if name not in suites:
        raise ValueError(
            f"Unknown review suite '{name}'. Available suites: {', '.join(list_review_suites())}"
        )
    return list(suites[name])


def resolve_review_selection(
    suite_name: str = "screening_ladder",
    review_keys: list[str] | None = None,
) -> list[ScreeningBenchmarkReview]:
    """Resolve a suite and optional subset of review keys (URLs)."""
    suite = get_review_suite(suite_name)
    if not review_keys:
        return suite

    review_by_key = {review.key: review for review in suite}
    unknown = [key for key in review_keys if key not in review_by_key]
    if unknown:
        raise ValueError(
            f"Unknown review key(s) for suite '{suite_name}': {', '.join(unknown)}"
        )
    return [review_by_key[key] for key in review_keys]


def _configuration_from_profile(profile_key: str, *, strict: bool = False) -> RoleModelMap:
    del strict  # catalogue lookup is always strict on unknown keys
    resolved = resolve_profile_agents(str(profile_key))
    return RoleModelMap(
        profile_key=resolved.profile_key,
        agents=resolved.agents,
        label=resolved.label,
    )


def expand_suite_run_config(
    suite_name: str,
    *,
    profiles_override: list[str] | None = None,
    repeats_override: int | None = None,
    batch_size_override: int | None = ...,  # type: ignore[assignment]
    mode_override: str | None = None,
) -> SuiteRunConfig:
    """
    Expand a suite's ``run.profiles`` list, applying optional CLI overrides.

    Runs reference **profiles only**. Models are leaf connections inside
    ``model_profiles.json``; profiles map roles onto those model keys.

    ``batch_size_override`` uses ``...`` as sentinel so ``None`` can mean
    "all studies" when explicitly passed.
    """
    raw = _raw_suite_by_name().get(suite_name)
    if raw is None:
        raise ValueError(
            f"Unknown review suite '{suite_name}'. "
            f"Available suites: {', '.join(list_review_suites())}"
        )

    run_block = dict(raw.get("run") or {})

    if profiles_override is not None:
        run_block["profiles"] = list(profiles_override)
    if repeats_override is not None:
        run_block["repeats"] = repeats_override
    if batch_size_override is not ...:
        run_block["batch_size"] = batch_size_override
    if mode_override is not None:
        run_block["mode"] = mode_override

    profiles_raw = run_block.get("profiles") or []
    if not profiles_raw:
        raise ValueError(
            f"Suite '{suite_name}' has no run.profiles. "
            "Pass --profiles on the CLI or add a run.profiles list to suites.json."
        )

    configurations = [
        _configuration_from_profile(str(key), strict=False) for key in profiles_raw
    ]

    # Prefer ``mode``; accept legacy ``stages`` in suites.json.
    mode = run_block.get("mode") or run_block.get("stages") or "screening-only"
    return SuiteRunConfig(
        configurations=configurations,
        repeats=int(run_block.get("repeats") or 1),
        batch_size=run_block.get("batch_size"),
        mode=str(mode),
    )
