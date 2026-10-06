"""
HTML comparison report generation for paired screening benchmark policies.
"""

from __future__ import annotations

import csv
import html
import json
from collections import Counter, defaultdict
from pathlib import Path

from bastirr.benchmarking.model_presets import get_model_preset

COMPARISON_REPORT_FILENAME = "screening_policy_comparison.html"


_COMPARISON_CSS = """
    :root {
      --bg: #f5efe3;
      --bg-soft: #fbf7ef;
      --ink: #1d2433;
      --muted: #5e6678;
      --line: rgba(29, 36, 51, 0.12);
      --card: rgba(255, 252, 246, 0.8);
      --include: #1b7f79;
      --include-soft: #bce6dc;
      --exclude: #b4512d;
      --exclude-soft: #f4ccb1;
      --navy: #223a5e;
      --gold: #d4a53a;
      --rose: #d96f4c;
      --shadow: 0 18px 40px rgba(44, 37, 24, 0.12);
      --radius: 24px;
    }

    * { box-sizing: border-box; }
    html { scroll-behavior: smooth; }

    body {
      margin: 0;
      color: var(--ink);
      background:
        radial-gradient(circle at top left, rgba(27, 127, 121, 0.18), transparent 32%),
        radial-gradient(circle at top right, rgba(212, 165, 58, 0.16), transparent 26%),
        linear-gradient(180deg, #f8f3e8 0%, #f4ede0 34%, #f7f2e9 100%);
      font-family: "Avenir Next", "Gill Sans", "Trebuchet MS", sans-serif;
      line-height: 1.5;
    }

    h1, h2, h3 {
      margin: 0;
      font-family: Georgia, "Palatino Linotype", "Book Antiqua", serif;
      letter-spacing: -0.02em;
    }

    p { margin: 0; }
    a { color: inherit; }

    .page {
      width: min(1200px, calc(100vw - 32px));
      margin: 0 auto;
      padding: 28px 0 56px;
    }

    .hero {
      position: relative;
      overflow: hidden;
      border: 1px solid rgba(29, 36, 51, 0.08);
      border-radius: 34px;
      padding: 34px;
      background:
        linear-gradient(135deg, rgba(255, 251, 244, 0.96), rgba(246, 238, 224, 0.9)),
        linear-gradient(135deg, rgba(27, 127, 121, 0.08), rgba(180, 81, 45, 0.06));
      box-shadow: var(--shadow);
    }

    .hero::after {
      content: "";
      position: absolute;
      inset: auto -80px -80px auto;
      width: 260px;
      height: 260px;
      border-radius: 999px;
      background: radial-gradient(circle, rgba(212, 165, 58, 0.24), transparent 68%);
      pointer-events: none;
    }

    .eyebrow {
      display: inline-flex;
      align-items: center;
      gap: 10px;
      margin-bottom: 16px;
      padding: 8px 14px;
      border-radius: 999px;
      background: rgba(255, 255, 255, 0.7);
      color: var(--muted);
      font-size: 0.86rem;
      text-transform: uppercase;
      letter-spacing: 0.08em;
    }

    .hero h1 {
      font-size: clamp(2.25rem, 4vw, 3.55rem);
      line-height: 0.98;
      max-width: 15ch;
      margin-bottom: 14px;
    }

    .hero-grid {
      display: grid;
      grid-template-columns: minmax(0, 1.08fr) minmax(340px, 0.92fr);
      gap: 28px;
      align-items: start;
    }

    .hero-copy { display: grid; gap: 18px; }

    .hero-copy p {
      max-width: 65ch;
      color: var(--muted);
      font-size: 1.04rem;
    }

    .hero-side {
      display: grid;
      gap: 10px;
      align-content: start;
    }

    .hero-model {
      display: grid;
      gap: 6px;
      justify-items: start;
      align-content: start;
      min-height: 0;
      padding: 0;
    }

    .hero-model .k {
      color: var(--muted);
      font-size: 0.78rem;
      text-transform: uppercase;
      letter-spacing: 0.09em;
      font-weight: 700;
    }

    .hero-model .v {
      color: var(--ink);
      font-family: Georgia, "Palatino Linotype", "Book Antiqua", serif;
      font-size: clamp(1.45rem, 2.4vw, 2.2rem);
      line-height: 1.02;
      font-weight: 700;
      letter-spacing: -0.02em;
      max-width: 14ch;
      text-wrap: pretty;
    }

    .badge-row, .source-row {
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
    }

    .source-row {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 10px 14px;
    }

    .badge, .source-link {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      padding: 10px 14px;
      border-radius: 999px;
      border: 1px solid rgba(29, 36, 51, 0.08);
      background: rgba(255, 255, 255, 0.72);
      color: var(--ink);
      text-decoration: none;
      font-size: 0.93rem;
    }

    .hero-stat-panel {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 14px;
    }

    .hero-stat {
      padding: 16px 18px;
      border-radius: 20px;
      background: rgba(255, 255, 255, 0.68);
      border: 1px solid rgba(29, 36, 51, 0.08);
    }

    .hero-stat .label {
      font-size: 0.8rem;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      color: var(--muted);
    }

    .hero-stat .value {
      margin-top: 4px;
      font-size: 1.8rem;
      font-weight: 700;
      color: var(--navy);
    }

    .hero-stat .note {
      margin-top: 6px;
      font-size: 0.9rem;
      color: var(--muted);
    }

    .section {
      margin-top: 28px;
      padding: 28px;
      border-radius: var(--radius);
      border: 1px solid rgba(29, 36, 51, 0.08);
      background: var(--card);
      backdrop-filter: blur(10px);
      box-shadow: var(--shadow);
    }

    .section-header {
      display: flex;
      justify-content: space-between;
      gap: 16px;
      align-items: end;
      margin-bottom: 22px;
    }

    .section-header p {
      max-width: 72ch;
      color: var(--muted);
    }

    .grid-2 {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 18px;
    }

    .policy-card {
      position: relative;
      overflow: hidden;
      padding: 22px;
      border-radius: 24px;
      border: 1px solid rgba(29, 36, 51, 0.08);
      background: rgba(255, 255, 255, 0.78);
    }

    .policy-card.include::before,
    .policy-card.exclude::before {
      content: "";
      position: absolute;
      inset: 0 auto 0 0;
      width: 6px;
      border-radius: 24px 0 0 24px;
    }

    .policy-card.include::before {
      background: linear-gradient(180deg, var(--include), #104f4c);
    }

    .policy-card.exclude::before {
      background: linear-gradient(180deg, var(--exclude), #6f2a13);
    }

    .policy-card h3 { font-size: 1.5rem; }

    .policy-subtitle {
      margin-top: 4px;
      color: var(--muted);
      font-size: 0.96rem;
    }

    .policy-story {
      margin-top: 16px;
      color: var(--ink);
      font-size: 1rem;
    }

    .metric-grid {
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 12px;
      margin-top: 18px;
    }

    .metric-chip {
      display: grid;
      padding: 12px;
      border-radius: 16px;
      background: var(--bg-soft);
      border: 1px solid rgba(29, 36, 51, 0.06);
    }

    .metric-chip .k {
      min-height: 2.4em;
      display: flex;
      align-items: flex-start;
      font-size: 0.78rem;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      color: var(--muted);
    }

    .metric-chip .v {
      margin-top: 2px;
      font-size: 1.35rem;
      font-weight: 700;
    }

    .micro-grid {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 12px;
      margin-top: 18px;
    }

    .micro-cell {
      min-height: 92px;
      padding: 14px;
      border-radius: 18px;
      color: white;
      display: grid;
      align-content: start;
      gap: 2px;
    }

    .micro-cell.light { color: var(--ink); }

    .micro-cell .cell-label {
      font-size: 0.78rem;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      opacity: 0.82;
    }

    .micro-cell .cell-value {
      font-size: 1.65rem;
      font-weight: 700;
    }

    .micro-cell .cell-note {
      font-size: 0.9rem;
      opacity: 0.88;
    }

    .viz-card {
      padding: 18px;
      border-radius: 22px;
      border: 1px solid rgba(29, 36, 51, 0.08);
      background: rgba(255, 255, 255, 0.72);
    }

    .viz-card h3 {
      font-size: 1.18rem;
      margin-bottom: 6px;
    }

    .viz-card p {
      margin-bottom: 14px;
      color: var(--muted);
      font-size: 0.95rem;
    }

    .chart {
      width: 100%;
      min-height: 300px;
    }

    .legend {
      display: flex;
      flex-wrap: wrap;
      gap: 12px;
      margin-top: 12px;
    }

    .legend-item {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      color: var(--muted);
      font-size: 0.9rem;
    }

    .swatch {
      width: 12px;
      height: 12px;
      border-radius: 999px;
      display: inline-block;
    }

    table {
      width: 100%;
      border-collapse: collapse;
      font-size: 0.95rem;
    }

    th, td {
      padding: 12px 10px;
      border-bottom: 1px solid var(--line);
      text-align: left;
      vertical-align: top;
    }

    th {
      color: var(--muted);
      font-size: 0.82rem;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      font-weight: 700;
    }

    .footer-note {
      margin-top: 16px;
      color: var(--muted);
      font-size: 0.92rem;
    }

    .error-policy-block + .error-policy-block {
      margin-top: 20px;
    }

    .error-policy-header {
      display: flex;
      justify-content: space-between;
      gap: 14px;
      align-items: baseline;
      margin-bottom: 10px;
    }

    .error-policy-total {
      color: var(--muted);
      font-size: 0.96rem;
      white-space: nowrap;
    }

    .stacked-bar {
      position: relative;
      height: 20px;
      border-radius: 999px;
      overflow: hidden;
      background: rgba(29, 36, 51, 0.08);
    }

    .error-rows {
      display: grid;
      gap: 8px;
      margin-top: 12px;
    }

    .error-row {
      display: grid;
      grid-template-columns: minmax(0, 1fr) auto;
      gap: 12px;
      align-items: center;
    }

    .error-label {
      display: inline-flex;
      align-items: center;
      gap: 10px;
      color: var(--muted);
    }

    .error-value {
      font-weight: 700;
      white-space: nowrap;
    }

    @media (max-width: 980px) {
      .grid-2,
      .metric-grid {
        grid-template-columns: 1fr;
      }

      .hero-stat-panel {
        grid-template-columns: 1fr 1fr;
      }

      .section-header {
        display: grid;
      }
    }

    @media (max-width: 720px) {
      .hero-grid {
        grid-template-columns: 1fr;
      }
    }

    @media (max-width: 560px) {
      .source-row {
        grid-template-columns: 1fr;
      }
    }

    @media (max-width: 640px) {
      .page {
        width: min(100vw - 20px, 1200px);
        padding-top: 14px;
      }

      .hero,
      .section {
        padding: 20px;
        border-radius: 24px;
      }

      .hero-model {
        min-height: 0;
      }

      .hero-stat-panel,
      .micro-grid {
        grid-template-columns: 1fr;
      }
    }
"""


def _load_json(path: Path) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _load_csv(path: Path) -> list[dict]:
    with open(path, "r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def _as_bool(value) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() == "true"


def _as_float(value, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _as_int(value, default: int = 0) -> int:
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return default


def _display_gatekeeper_model(label: str) -> str:
    normalized = str(label).strip()
    if not normalized:
        return normalized
    if "[" in normalized and normalized.endswith("]"):
        _prefix, bracket_part = normalized.rsplit("[", 1)
        bracket_value = bracket_part[:-1].strip()
        if bracket_value:
            return bracket_value
    return normalized


def _report_gatekeeper_name_from_preset(preset_key: str) -> str:
    preset = get_model_preset(preset_key).resolve(strict=False)
    return preset.description or _display_gatekeeper_model(preset.model_label)


def _unique_in_order(values: list[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for value in values:
        normalized = str(value).strip()
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        ordered.append(normalized)
    return ordered


def _load_policy_payload(policy_dir: Path) -> dict:
    summary = _load_json(policy_dir / "summary.json")
    runs = _load_csv(policy_dir / "summary.csv")
    scored_runs = [run for run in runs if _as_bool(run.get("scored_for_aggregate"))]
    leaderboard = summary.get("leaderboard", [])
    review_rows = sorted(
        summary.get("review_leaderboard", []),
        key=lambda row: (_as_int(row.get("n_studies")), str(row.get("review_key", ""))),
    )
    overall = leaderboard[0] if leaderboard else {}
    confusion = {
        "tp": sum(_as_int(run.get("tp")) for run in scored_runs),
        "fp": sum(_as_int(run.get("fp")) for run in scored_runs),
        "tn": sum(_as_int(run.get("tn")) for run in scored_runs),
        "fn": sum(_as_int(run.get("fn")) for run in scored_runs),
    }
    error_counts: Counter[tuple[str, str]] = Counter()
    for run in scored_runs:
        inspection_path = Path(run.get("screening_inspection_json", ""))
        if not inspection_path.exists():
            continue
        payload = _load_json(inspection_path)
        for study in payload.get("studies", []):
            predicted = str(study.get("predicted_decision") or "").strip().upper()
            gold = str(study.get("gold_screening_decision") or "").strip().upper()
            if not predicted or predicted == gold:
                continue
            key = (
                str(study.get("gold_label", "")),
                str(study.get("gold_review_outcome", "")),
            )
            error_counts[key] += 1
    total_error_count = sum(error_counts.values())
    review_lookup = {
        str(row.get("review_key", "")): {
            "key": str(row.get("review_key", "")),
            "label": str(row.get("review_key", "")).replace("_", " "),
            "studies": _as_int(row.get("n_studies")),
            "f1": _as_float(row.get("mean_f1")),
            "recall": _as_float(row.get("mean_recall")),
            "review_title": str(row.get("review_title", "")),
            "gold_pass_count": _as_int(row.get("gold_pass_count")),
        }
        for row in review_rows
    }
    return {
        "dir": policy_dir,
        "policy": summary.get("gold_label_policy", policy_dir.name),
        "summary": summary,
        "runs": runs,
        "scored_runs": scored_runs,
        "overall": overall,
        "micro": confusion,
        "error_counts": error_counts,
        "total_errors": total_error_count,
        "reviews": review_lookup,
    }


def _policy_role(policy_name: str) -> tuple[str, str]:
    if policy_name == "include_label_0_5":
        return "include", "Screening-friendly policy"
    return "exclude", "Strict final-inclusion proxy"


def _error_label(gold_label: str, outcome: str) -> str:
    return f"{gold_label} \u2192 {outcome.replace('_', ' ')}"


def _render_links(experiment_dir: Path) -> str:
    links = []
    ordered_pairs = [
        ("summary.csv", "summary.csv"),
        ("summary.json", "summary.json"),
        ("screening_results_summary.html", "report"),
    ]
    ordered_policies = [
        ("exclude_policy", "exclude"),
        ("include_policy", "include"),
    ]
    for filename, label in ordered_pairs:
        for policy_dir_name, policy_label in ordered_policies:
            policy_dir = experiment_dir / policy_dir_name
            if (policy_dir / filename).exists():
                links.append(
                    f'<a class="source-link" href="./{html.escape(policy_dir.name)}/{html.escape(filename)}">{html.escape(policy_label)} {html.escape(label)}</a>'
                )
    return "\n".join(f"            {link}" for link in links)


def _gatekeeper_model_summary(*payloads: dict) -> dict | None:
    preset_keys = _unique_in_order(
        [
            str(row.get("gatekeeper_preset", ""))
            for payload in payloads
            for row in payload["summary"].get("leaderboard", [])
        ]
        + [
            str(run.get("gatekeeper_preset", ""))
            for payload in payloads
            for run in payload["runs"]
        ]
    )
    labels: list[str] = []
    for preset_key in preset_keys:
        try:
            labels.append(_report_gatekeeper_name_from_preset(preset_key))
        except ValueError:
            continue
    if not labels:
        labels = _unique_in_order(
            [
                str(row.get("gatekeeper_model_label", ""))
                for payload in payloads
                for row in payload["summary"].get("leaderboard", [])
            ]
            + [
                str(run.get("gatekeeper_model_label", ""))
                for payload in payloads
                for run in payload["runs"]
            ]
        )
    if not labels:
        return None
    if len(labels) == 1:
        return {
            "label": "Gatekeeper model",
            "value": _display_gatekeeper_model(labels[0]),
        }
    return {
        "label": "Gatekeeper models",
        "value": ", ".join(_display_gatekeeper_model(label) for label in labels),
    }


def _build_comparison_payload(experiment_dir: Path) -> dict:
    include_dir = experiment_dir / "include_policy"
    exclude_dir = experiment_dir / "exclude_policy"
    if not include_dir.exists() or not exclude_dir.exists():
        raise FileNotFoundError(
            f"Expected include_policy and exclude_policy inside: {experiment_dir}"
        )

    include = _load_policy_payload(include_dir)
    exclude = _load_policy_payload(exclude_dir)
    policy_payloads = {"include": include, "exclude": exclude}

    review_order = sorted(
        set(include["reviews"]) | set(exclude["reviews"]),
        key=lambda key: include["reviews"].get(key, exclude["reviews"][key])["studies"],
    )
    review_rows = []
    for review_key in review_order:
        include_review = include["reviews"][review_key]
        exclude_review = exclude["reviews"][review_key]
        review_rows.append({
            "key": review_key,
            "label": include_review["label"],
            "studies": include_review["studies"],
            "include_f1": include_review["f1"],
            "include_recall": include_review["recall"],
            "exclude_f1": exclude_review["f1"],
            "exclude_recall": exclude_review["recall"],
        })
    exclude_recall = exclude["overall"].get("mean_recall", 0.0)
    include_recall = include["overall"].get("mean_recall", 0.0)
    if exclude_recall is not None and include_recall is not None:
        recall_swing = exclude_recall- include_recall
    else:
        recall_swing = None

    exclude_f1 = exclude["overall"].get("mean_f1", 0.0)
    include_f1 = include["overall"].get("mean_f1", 0.0)
    if exclude_f1 is not None and include_f1 is not None:
        f1_swing = exclude_f1 - include_f1
    else:
        f1_swing = None
    largest_recall_row = max(
        review_rows,
        key=lambda row: abs(row["exclude_recall"] - row["include_recall"]),
    ) if review_rows else None

    hero_stats = [
        {
            "label": "Macro recall swing",
            "value": f"{round(recall_swing * 100)} pts" if recall_swing is not None else "n/a",
            "note": "Change in macro recall when label 0.5 is scored as EXCLUDE instead of INCLUDE.",
        },
        {
            "label": "Macro F1 swing",
            "value": f"{round(f1_swing * 100)} pts" if f1_swing is not None else "n/a",
            "note": "Change in macro F1 across the same raw screening runs.",
        },
        {
            "label": "Largest review recall delta",
            "value": (
                f"{largest_recall_row['label']} ({round(abs(largest_recall_row['exclude_recall'] - largest_recall_row['include_recall']) * 100)} pts)"
                if largest_recall_row else "n/a"
            ),
            "note": "Review with the biggest policy-driven movement in mean recall.",
        },
        {
            "label": "Shared raw run bundle",
            "value": f"{len(include['runs'])} runs",
            "note": "Both policy views are scored from the same saved screening decisions.",
        },
    ]

    cards = []
    for role, payload in policy_payloads.items():
        role_key, short = _policy_role(payload["policy"])
        micro = payload["micro"]
        total_micro = sum(micro.values()) or 1
        cards.append({
            "role": role_key,
            "policy": payload["policy"],
            "short": short,
            "folder": payload["dir"].name,
            "story": (
                "Treats label 0.5 as screen-positive, which is closer to permissive title/abstract screening."
                if payload["policy"] == "include_label_0_5"
                else "Treats label 0.5 as screen-negative, which is closer to a stricter downstream inclusion proxy."
            ),
            "metrics": [
                ["Macro F1", payload["overall"].get("mean_f1", 0.0)],
                ["Macro recall", payload["overall"].get("mean_recall", 0.0)],
                ["Macro precision", payload["overall"].get("mean_precision", 0.0)],
                ["Macro accuracy", payload["overall"].get("mean_accuracy", 0.0)],
            ],
            "micro_cells": [
                {"label": "True positive", "value": micro["tp"], "note": micro["tp"] / total_micro, "bg": "var(--include)" if role_key == "include" else "var(--navy)"},
                {"label": "False negative", "value": micro["fn"], "note": micro["fn"] / total_micro, "bg": "var(--rose)"},
                {"label": "False positive", "value": micro["fp"], "note": micro["fp"] / total_micro, "bg": "var(--gold)", "light": True},
                {"label": "True negative", "value": micro["tn"], "note": micro["tn"] / total_micro, "bg": "var(--navy)" if role_key == "include" else "var(--include)"},
            ],
        })

    def error_breakdown(payload: dict, color: str) -> list[dict]:
        rows = []
        palette = [color, "#223a5e", "#d4a53a", "#d96f4c", "#8e9aaf"]
        for idx, ((gold_label, outcome), count) in enumerate(payload["error_counts"].most_common(4)):
            rows.append({
                "label": _error_label(gold_label, outcome),
                "errors": count,
                "color": palette[idx % len(palette)],
            })
        return rows

    comparison = {
        "title": "Screening Benchmark Policy Comparison",
        "title_html": "Screening Benchmark<br>Policy Comparison",
        "eyebrow": "Benchmark presentation • same screening runs • two label policies",
        "experiment": experiment_dir.name,
        "gatekeeper_model": _gatekeeper_model_summary(include, exclude),
        "hero_paragraph": (
            "These two benchmark views use the same review set and the same screening decisions, "
            "but they score label 0.5 differently. The comparison below shows how that single "
            "evaluation choice changes the apparent strengths and weaknesses of the screener."
        ),
        "badges": [
            f"{len(review_rows)} reviews",
            f"{len(include['runs'])} attempted runs per policy",
            "same saved screening decisions",
        ],
        "hero_stats": hero_stats,
        "links_html": _render_links(experiment_dir),
        "section_copy": {
            "policy_cards": (
                "These cards summarize the two scoring lenses side by side. "
                "The underlying raw screening outputs are the same; only the interpretation of label 0.5 changes."
            ),
            "metric_move": (
                "These view-by-review comparisons show where the policy choice creates real movement, "
                "rather than just shifting the overall average."
            ),
            "error_composition": (
                "This view shows which underlying dataset outcomes are driving the mistakes under each policy, "
                "not just how many mistakes there are."
            ),
            "review_table": (
                "The table below keeps the two policies aligned review by review so the metric shifts stay easy to inspect."
            ),
        },
        "policies": {
            "include": {
                "name": include["policy"],
                "short": _policy_role(include["policy"])[1],
                "folder": include["dir"].name,
                "story": cards[0]["story"],
                "overall": include["overall"],
                "micro": include["micro"],
                "reviews": [include["reviews"][key] for key in review_order],
                "errorBreakdown": error_breakdown(include, "var(--include)"),
            },
            "exclude": {
                "name": exclude["policy"],
                "short": _policy_role(exclude["policy"])[1],
                "folder": exclude["dir"].name,
                "story": cards[1]["story"],
                "overall": exclude["overall"],
                "micro": exclude["micro"],
                "reviews": [exclude["reviews"][key] for key in review_order],
                "errorBreakdown": error_breakdown(exclude, "var(--exclude)"),
            },
        },
        "policyCards": cards,
        "reviewRows": review_rows,
    }
    return comparison


def _comparison_html(payload: dict) -> str:
    data_json = json.dumps({
        "policies": payload["policies"],
        "policyCards": payload["policyCards"],
        "reviewRows": payload["reviewRows"],
        "heroStats": payload["hero_stats"],
    }, ensure_ascii=False, indent=2)
    badge_html = "\n".join(
        f'            <span class="badge">{html.escape(text)}</span>'
        for text in payload["badges"]
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{html.escape(payload["title"])}</title>
  <style>
{_COMPARISON_CSS}
  </style>
</head>
<body>
  <main class="page">
    <header class="hero">
      <div class="eyebrow">{html.escape(payload["eyebrow"])}</div>
      <div class="hero-grid">
        <div class="hero-copy">
          <h1>{payload["title_html"]}</h1>
          <p>
            {html.escape(payload["hero_paragraph"])}
          </p>
          <div class="badge-row">
{badge_html}
          </div>
          <div class="source-row">
{payload["links_html"]}
          </div>
        </div>
        <div class="hero-side">
          {f'''<div class="hero-model"><div class="k">{html.escape(payload["gatekeeper_model"]["label"])}</div><div class="v">{html.escape(payload["gatekeeper_model"]["value"])}</div></div>''' if payload.get("gatekeeper_model") else ""}
          <div class="hero-stat-panel" id="hero-stats"></div>
        </div>
      </div>
    </header>

    <section class="section">
      <div class="section-header">
        <div>
          <h2>Policy cards</h2>
        </div>
        <p>
          {html.escape(payload["section_copy"]["policy_cards"])}
        </p>
      </div>
      <div class="grid-2" id="policy-cards"></div>
    </section>

    <section class="section">
      <div class="section-header">
        <div>
          <h2>Where the metrics move</h2>
        </div>
        <p>
          {html.escape(payload["section_copy"]["metric_move"])}
        </p>
      </div>
      <div class="grid-2">
        <div class="viz-card">
          <h3>Recall by review</h3>
          <p>Each pair compares the same review under the two label policies.</p>
          <div id="recall-chart" class="chart"></div>
          <div class="legend">
            <span class="legend-item"><span class="swatch" style="background: var(--include);"></span> include_label_0_5</span>
            <span class="legend-item"><span class="swatch" style="background: var(--exclude);"></span> exclude_label_0_5</span>
          </div>
        </div>
        <div class="viz-card">
          <h3>F1 by review</h3>
          <p>This makes the policy effect visible without collapsing it into one overall average.</p>
          <div id="f1-chart" class="chart"></div>
          <div class="legend">
            <span class="legend-item"><span class="swatch" style="background: var(--include);"></span> include_label_0_5</span>
            <span class="legend-item"><span class="swatch" style="background: var(--exclude);"></span> exclude_label_0_5</span>
          </div>
        </div>
      </div>
    </section>

    <section class="section">
      <div class="section-header">
        <div>
          <h2>Error composition</h2>
        </div>
        <p>
          {html.escape(payload["section_copy"]["error_composition"])}
        </p>
      </div>
      <div class="viz-card">
        <h3>Error mix by policy</h3>
        <p>Each stacked bar partitions total misclassifications by underlying dataset outcome.</p>
        <div id="error-composition"></div>
      </div>
    </section>

    <section class="section">
      <div class="section-header">
        <div>
          <h2>Review-by-review comparison</h2>
        </div>
        <p>
          {html.escape(payload["section_copy"]["review_table"])}
        </p>
      </div>
      <div class="viz-card">
        <table>
          <thead>
            <tr>
              <th>Review</th>
              <th>Studies</th>
              <th>Include policy F1</th>
              <th>Include policy recall</th>
              <th>Exclude policy F1</th>
              <th>Exclude policy recall</th>
            </tr>
          </thead>
          <tbody id="review-table"></tbody>
        </table>
      </div>
      <p class="footer-note">
        Table values are macro means over scored runs in each policy folder.
      </p>
    </section>
  </main>

  <script>
    const data = {data_json};

    const fmtPct = value => `${{(value * 100).toFixed(1)}}%`;
    const fmtPctShort = value => `${{(value * 100).toFixed(0)}}%`;
    const fmtNum = value => Number(value).toLocaleString();

    function heroStats() {{
      const mount = document.getElementById("hero-stats");
      mount.innerHTML = data.heroStats.map(stat => `
        <div class="hero-stat">
          <div class="label">${{stat.label}}</div>
          <div class="value">${{stat.value}}</div>
          <div class="note">${{stat.note}}</div>
        </div>
      `).join("");
    }}

    function policyCards() {{
      const mount = document.getElementById("policy-cards");
      mount.innerHTML = data.policyCards.map(card => `
        <article class="policy-card ${{card.role}}">
          <h3>${{card.policy}}</h3>
          <div class="policy-subtitle">${{card.short}} • folder <code>${{card.folder}}</code></div>
          <p class="policy-story">${{card.story}}</p>
          <div class="metric-grid">
            ${{card.metrics.map(([k, v]) => `
              <div class="metric-chip">
                <div class="k">${{k}}</div>
                <div class="v">${{fmtPct(v)}}</div>
              </div>
            `).join("")}}
          </div>
          <div class="micro-grid">
            ${{card.micro_cells.map(cell => `
              <div class="micro-cell ${{cell.light ? "light" : ""}}" style="background:${{cell.bg}}">
                <div class="cell-label">${{cell.label}}</div>
                <div class="cell-value">${{fmtNum(cell.value)}}</div>
                  <div class="cell-note">${{fmtPct(cell.note)}} of pooled decisions</div>
              </div>
            `).join("")}}
          </div>
        </article>
      `).join("");
    }}

    function renderDumbbell(mountId, metric) {{
      const mount = document.getElementById(mountId);
      const width = mount.clientWidth || 520;
      const rowHeight = 58;
      const margin = {{ top: 20, right: 24, bottom: 36, left: 180 }};
      const innerWidth = width - margin.left - margin.right;
      const height = margin.top + margin.bottom + rowHeight * data.reviewRows.length;
      const lines = [];

      data.reviewRows.forEach((row, index) => {{
        const y = margin.top + rowHeight * index + 18;
        const includeValue = row[`include_${{metric}}`];
        const excludeValue = row[`exclude_${{metric}}`];
        const x1 = margin.left + innerWidth * includeValue;
        const x2 = margin.left + innerWidth * excludeValue;
        const left = Math.min(x1, x2);
        const right = Math.max(x1, x2);
        lines.push(`
          <text x="${{margin.left - 12}}" y="${{y + 4}}" text-anchor="end" fill="#5e6678" font-size="13">${{row.label}}</text>
          <line x1="${{left}}" y1="${{y}}" x2="${{right}}" y2="${{y}}" stroke="#b8b1a1" stroke-width="3" stroke-linecap="round"></line>
          <circle cx="${{x1}}" cy="${{y}}" r="8" fill="var(--include)"></circle>
          <circle cx="${{x2}}" cy="${{y}}" r="8" fill="var(--exclude)"></circle>
          <text x="${{x1}}" y="${{y - 14}}" text-anchor="middle" fill="var(--include)" font-size="12" font-weight="700">${{fmtPctShort(includeValue)}}</text>
          <text x="${{x2}}" y="${{y + 24}}" text-anchor="middle" fill="var(--exclude)" font-size="12" font-weight="700">${{fmtPctShort(excludeValue)}}</text>
        `);
      }});

      const ticks = [0, 0.25, 0.5, 0.75, 1.0].map(value => {{
        const x = margin.left + innerWidth * value;
        return `
          <line x1="${{x}}" y1="${{margin.top - 8}}" x2="${{x}}" y2="${{height - margin.bottom + 8}}" stroke="rgba(29,36,51,0.1)" stroke-width="1"></line>
          <text x="${{x}}" y="${{height - 10}}" text-anchor="middle" fill="#5e6678" font-size="12">${{fmtPctShort(value)}}</text>
        `;
      }}).join("");

      mount.innerHTML = `
        <svg viewBox="0 0 ${{width}} ${{height}}" width="100%" height="${{height}}">
          ${{ticks}}
          ${{lines.join("")}}
        </svg>
      `;
    }}

    function renderErrorComposition() {{
      const mount = document.getElementById("error-composition");
      const policies = ["include", "exclude"];
      mount.innerHTML = policies.map(key => {{
        const policy = data.policies[key];
        const total = policy.errorBreakdown.reduce((sum, item) => sum + item.errors, 0) || 1;
        let cursor = 0;
        const bar = policy.errorBreakdown.map(item => {{
          const width = (item.errors / total) * 100;
          const segment = `
            <div style="position:absolute;left:${{cursor}}%;top:0;width:${{width}}%;height:100%;background:${{item.color}};"></div>
          `;
          cursor += width;
          return segment;
        }}).join("");

        const legend = policy.errorBreakdown.map(item => `
          <div class="error-row">
            <div class="error-label">
              <span class="swatch" style="background:${{item.color}};"></span>
              ${{item.label}}
            </div>
            <div class="error-value">${{item.errors}} • ${{fmtPct(item.errors / total)}}</div>
          </div>
        `).join("");

        return `
          <div class="error-policy-block">
            <div class="error-policy-header">
              <div style="font-weight:700;">${{policy.name}}</div>
              <div class="error-policy-total">${{total}} total errors</div>
            </div>
            <div class="stacked-bar">
              ${{bar}}
            </div>
            <div class="error-rows">
              ${{legend}}
            </div>
          </div>
        `;
      }}).join("");
    }}

    function renderReviewTable() {{
      document.getElementById("review-table").innerHTML = data.reviewRows.map(row => `
        <tr>
          <td><strong>${{row.label}}</strong></td>
          <td>${{row.studies}}</td>
          <td>${{fmtPct(row.include_f1)}}</td>
          <td>${{fmtPct(row.include_recall)}}</td>
          <td>${{fmtPct(row.exclude_f1)}}</td>
          <td>${{fmtPct(row.exclude_recall)}}</td>
        </tr>
      `).join("");
    }}

    heroStats();
    policyCards();
    renderDumbbell("recall-chart", "recall");
    renderDumbbell("f1-chart", "f1");
    renderErrorComposition();
    renderReviewTable();
  </script>
</body>
</html>
"""


def write_policy_comparison_report(experiment_dir: Path) -> dict:
    experiment_dir = Path(experiment_dir)
    payload = _build_comparison_payload(experiment_dir)
    report_path = experiment_dir / COMPARISON_REPORT_FILENAME
    report_path.write_text(_comparison_html(payload), encoding="utf-8")
    return {
        "report_path": str(report_path),
        "title": payload["title"],
    }
