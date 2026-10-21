"""Read screening decisions from Mentor run artifacts (evidence.json)."""

from __future__ import annotations

import json
import os
from pathlib import Path


def read_existing_decisions(output_dir: str | os.PathLike[str]) -> list[dict]:
    path = Path(output_dir) / "evidence.json"
    if not path.exists():
        return []
    with open(path, encoding="utf-8") as f:
        payload = json.load(f)
    decisions = payload.get("screening_decisions", [])
    return decisions if isinstance(decisions, list) else []
