"""Repo paths for experiments (no Mentor imports)."""

from __future__ import annotations

from pathlib import Path


def _find_project_root() -> Path:
    here = Path(__file__).resolve().parent
    for candidate in (here, *here.parents):
        if (candidate / "pyproject.toml").exists():
            return candidate
    return here.parent


PROJECT_ROOT = _find_project_root()
INPUT_DIR = PROJECT_ROOT / "data" / "experiments" / "input"
OUTPUT_DIR = PROJECT_ROOT / "data" / "experiments" / "output"
DATASET_DIR = INPUT_DIR / "cochrane_sr_dataset"
MODEL_PROFILES_PATH = PROJECT_ROOT / "src" / "config" / "model_profiles.json"
