"""Write Mentor-compatible review JSON (no gold labels; no Mentor imports)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable


def normalize_mode(raw: Any) -> str:
    if raw is None or (isinstance(raw, str) and not str(raw).strip()):
        return "full"
    key = str(raw).strip().lower()
    if key in {"screening", "screening-only"}:
        return "screening-only"
    if key == "full":
        return "full"
    raise ValueError(f"mode must be 'full' or 'screening-only', got {raw!r}")


def write_review_json(
    path: str | Path,
    *,
    mode: str,
    title: str,
    objective: str,
    background: str,
    selection_criteria: str,
    studies: Iterable[Any] | None = None,
) -> Path:
    """Write one Mentor review JSON file.

    ``studies`` items need ``.title`` / ``.abstract`` attributes (or dicts).
    For ``mode=full``, studies are omitted.
    """
    resolved_mode = normalize_mode(mode)
    data: dict[str, Any] = {
        "mode": resolved_mode,
        "title": title,
        "objective": objective,
        "background": background,
        "selection_criteria": selection_criteria,
    }
    if resolved_mode == "screening-only":
        study_rows: list[dict[str, Any]] = []
        for i, study in enumerate(studies or []):
            if isinstance(study, dict):
                title_s = str(study.get("title") or "")
                abstract_s = str(study.get("abstract") or "")
            else:
                title_s = str(getattr(study, "title", "") or "")
                abstract_s = str(getattr(study, "abstract", "") or "")
            study_rows.append(
                {
                    "study_index": i + 1,
                    "title": title_s,
                    "abstract": abstract_s,
                }
            )
        if not study_rows:
            raise ValueError("mode=screening-only requires a non-empty studies list")
        data["studies"] = study_rows

    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return out
