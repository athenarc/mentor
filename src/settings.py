"""
Core Mentor settings: repo paths, timeouts, and shared env defaults.

Import-time side effect: loads ``.env`` from the repository root.
Domain-specific settings live elsewhere:

- ``mentor.runtime.models`` — model factory / resolve helpers
- ``mentor.tools.search.settings`` — Librarian search / MCP endpoints

Mentor run artifacts live under ``data/mentor/``. Cochrane dataset + suite
outputs live under ``data/experiments/`` (owned by the experiments package).
"""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv


def _find_project_root() -> Path:
    """Resolve the repository root (directory containing pyproject.toml)."""
    here = Path(__file__).resolve().parent
    for candidate in (here, *here.parents):
        if (candidate / "pyproject.toml").exists():
            return candidate
    return here.parent.parent


PROJECT_ROOT = _find_project_root()
load_dotenv(PROJECT_ROOT / ".env")

PACKAGE_DIR = Path(__file__).resolve().parent
# Single-review JSON examples and Mentor pipeline outputs.
INPUT_DIR = PROJECT_ROOT / "data" / "mentor" / "input"
OUTPUT_DIR = PROJECT_ROOT / "data" / "mentor" / "output"
REVIEWS_DIR = INPUT_DIR / "reviews"

# Per-step code execution timeout (smolagents local Python executor).
EXECUTOR_TIMEOUT_SECONDS = int(os.getenv("MENTOR_EXECUTOR_TIMEOUT", "500"))

# Per-model HTTP request timeout (separate from the code executor).
MODEL_REQUEST_TIMEOUT_SECONDS = int(os.getenv("MENTOR_MODEL_REQUEST_TIMEOUT", "900"))

# Shared model env defaults (used by ``mentor.runtime.models``).
MODEL_BACKEND = os.getenv("MENTOR_MODEL_BACKEND", "openai")
DEFAULT_MODEL_ID = os.getenv("MENTOR_MODEL", "gpt-5")
API_BASE = os.getenv("MENTOR_API_BASE", "")
API_KEY = os.getenv("MENTOR_API_KEY", "")
