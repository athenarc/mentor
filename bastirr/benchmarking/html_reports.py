"""
HTML report generation utilities for screening benchmark outputs.
"""

from __future__ import annotations

import csv
import html
import json
from collections import Counter, defaultdict
from pathlib import Path
from statistics import fmean, pstdev

from bastirr.benchmarking.comparison_reports import write_policy_comparison_report
from bastirr.benchmarking.model_presets import get_model_preset

HTML_REPORT_FILENAME = "screening_results_summary.html"

_REPORT_CSS = """
    :root {
      --bg: #f6f1e7;
      --bg-soft: #fcfaf5;
      --card: rgba(255, 253, 248, 0.84);
      --ink: #1e2430;
      --muted: #667084;
      --line: rgba(30, 36, 48, 0.1);
      --accent: #245a7a;
      --accent-soft: #c7deed;
      --accent-2: #c36b3c;
      --accent-3: #d8a93e;
      --good: #167a67;
      --warn: #ba6a2b;
      --shadow: 0 18px 42px rgba(55, 45, 28, 0.12);
      --radius: 24px;
    }

    * { box-sizing: border-box; }

    body {
      margin: 0;
      color: var(--ink);
      font-family: "Avenir Next", "Segoe UI", sans-serif;
      line-height: 1.5;
      background:
        radial-gradient(circle at top right, rgba(36, 90, 122, 0.12), transparent 26%),
        radial-gradient(circle at top left, rgba(195, 107, 60, 0.12), transparent 22%),
        linear-gradient(180deg, #f8f3ea 0%, #f3ede1 52%, #f7f3ec 100%);
    }

    h1, h2, h3 {
      margin: 0;
      font-family: Georgia, "Palatino Linotype", serif;
      letter-spacing: -0.02em;
    }

    p { margin: 0; }

    code {
      padding: 0.15em 0.35em;
      border-radius: 0.45em;
      background: rgba(36, 90, 122, 0.08);
      font-size: 0.92em;
    }

    .page {
      width: min(1180px, calc(100vw - 32px));
      margin: 0 auto;
      padding: 26px 0 56px;
    }

    .hero, .section {
      border-radius: 30px;
      border: 1px solid rgba(30, 36, 48, 0.08);
      background: var(--card);
      box-shadow: var(--shadow);
      backdrop-filter: blur(10px);
    }

    .hero {
      padding: 32px;
      overflow: hidden;
      position: relative;
    }

    .hero::after {
      content: "";
      position: absolute;
      width: 220px;
      height: 220px;
      right: -60px;
      bottom: -70px;
      border-radius: 999px;
      background: radial-gradient(circle, rgba(36, 90, 122, 0.18), transparent 68%);
      pointer-events: none;
    }

    .eyebrow {
      display: inline-flex;
      gap: 10px;
      align-items: center;
      margin-bottom: 14px;
      padding: 8px 12px;
      border-radius: 999px;
      background: rgba(255, 255, 255, 0.7);
      color: var(--muted);
      font-size: 0.83rem;
      letter-spacing: 0.08em;
      text-transform: uppercase;
    }

    .hero h1 {
      font-size: clamp(2.2rem, 4vw, 3.45rem);
      line-height: 0.98;
      margin-bottom: 12px;
      max-width: 16ch;
    }

    .hero-grid {
      display: grid;
      grid-template-columns: minmax(0, 1.12fr) minmax(320px, 0.88fr);
      gap: 26px;
      align-items: start;
    }

    .hero-copy {
      display: grid;
      gap: 18px;
    }

    .hero-copy p {
      max-width: 68ch;
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
      font-family: Georgia, "Palatino Linotype", serif;
      font-size: clamp(1.45rem, 2.4vw, 2.2rem);
      line-height: 1.02;
      font-weight: 700;
      letter-spacing: -0.02em;
      max-width: 14ch;
      text-wrap: pretty;
    }

    .link-row, .badge-row {
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
    }

    .link-row a, .badge {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      padding: 10px 14px;
      border-radius: 999px;
      text-decoration: none;
      color: inherit;
      border: 1px solid rgba(30, 36, 48, 0.08);
      background: rgba(255,255,255,0.74);
      font-size: 0.92rem;
    }

    .stat-grid {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 14px;
    }

    .stat {
      padding: 16px;
      border-radius: 18px;
      background: rgba(255,255,255,0.76);
      border: 1px solid rgba(30, 36, 48, 0.08);
    }

    .stat .label {
      color: var(--muted);
      font-size: 0.78rem;
      text-transform: uppercase;
      letter-spacing: 0.08em;
    }

    .stat .value {
      margin-top: 4px;
      font-size: 1.8rem;
      font-weight: 700;
      color: var(--accent);
    }

    .stat .note {
      margin-top: 6px;
      color: var(--muted);
      font-size: 0.9rem;
    }

    .section {
      margin-top: 26px;
      padding: 26px;
    }

    .section-header {
      display: flex;
      justify-content: space-between;
      gap: 18px;
      align-items: end;
      margin-bottom: 20px;
    }

    .section-header p {
      max-width: 72ch;
      color: var(--muted);
    }

    .grid-2 {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 18px;
      align-items: start;
    }

    .panel {
      padding: 18px;
      border-radius: 22px;
      border: 1px solid rgba(30, 36, 48, 0.08);
      background: rgba(255,255,255,0.74);
    }

    .panel h3 {
      font-size: 1.18rem;
      margin-bottom: 6px;
    }

    .panel p {
      color: var(--muted);
      font-size: 0.94rem;
      margin-bottom: 14px;
    }

    .mini-grid {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 12px;
    }

    .chip {
      padding: 12px;
      border-radius: 16px;
      background: var(--bg-soft);
      border: 1px solid rgba(30, 36, 48, 0.06);
    }

    .chip .k {
      color: var(--muted);
      font-size: 0.76rem;
      text-transform: uppercase;
      letter-spacing: 0.08em;
    }

    .chip .v {
      margin-top: 3px;
      font-size: 1.28rem;
      font-weight: 700;
    }

    .confusion-grid {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 10px;
      margin-top: 12px;
    }

    .confusion-cell {
      min-height: 92px;
      padding: 14px;
      border-radius: 18px;
      color: white;
      display: grid;
      gap: 2px;
      align-content: start;
    }

    .confusion-cell.light { color: var(--ink); }

    .cell-label {
      font-size: 0.78rem;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      opacity: 0.85;
    }

    .cell-value {
      font-size: 1.6rem;
      font-weight: 700;
    }

    .cell-note {
      font-size: 0.9rem;
      opacity: 0.9;
    }

    .chart {
      width: 100%;
      min-height: 320px;
    }

    table {
      width: 100%;
      border-collapse: collapse;
      font-size: 0.94rem;
    }

    .compact-table {
      table-layout: auto;
    }

    th, td {
      padding: 12px 10px;
      border-bottom: 1px solid var(--line);
      text-align: left;
      vertical-align: top;
    }

    th {
      color: var(--muted);
      font-size: 0.8rem;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      font-weight: 700;
    }

    .compact-table th,
    .compact-table td {
      padding: 10px 8px;
    }

    .numeric {
      white-space: nowrap;
    }

    .run-label {
      font-weight: 700;
      color: var(--ink);
    }

    .run-label small {
      display: block;
      margin-top: 2px;
      font-size: 0.82rem;
      font-weight: 500;
      color: var(--muted);
    }

    .study-list {
      display: grid;
      gap: 12px;
    }

    .study-item {
      padding: 16px;
      border-radius: 18px;
      background: rgba(255,255,255,0.76);
      border: 1px solid rgba(30, 36, 48, 0.08);
    }

    .study-head {
      display: flex;
      justify-content: space-between;
      gap: 12px;
      align-items: start;
      margin-bottom: 8px;
    }

    .study-ref {
      font-weight: 700;
      color: var(--accent);
    }

    .study-count {
      white-space: nowrap;
      padding: 6px 10px;
      border-radius: 999px;
      background: var(--bg-soft);
      color: var(--muted);
      font-size: 0.84rem;
    }

    .study-title {
      font-size: 0.96rem;
    }

    .pill-row {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      margin-top: 10px;
    }

    .pill {
      padding: 6px 10px;
      border-radius: 999px;
      border: 1px solid rgba(30, 36, 48, 0.08);
      background: rgba(255,255,255,0.8);
      color: var(--muted);
      font-size: 0.82rem;
    }

    .footer-note {
      margin-top: 14px;
      color: var(--muted);
      font-size: 0.92rem;
    }

    @media (max-width: 980px) {
      .grid-2, .mini-grid {
        grid-template-columns: 1fr;
      }

      .section-header {
        display: grid;
      }
    }

    @media (max-width: 700px) {
      .hero-grid {
        grid-template-columns: 1fr;
      }
    }

    @media (max-width: 640px) {
      .page {
        width: min(100vw - 18px, 1180px);
        padding-top: 14px;
      }

      .hero, .section {
        padding: 20px;
        border-radius: 24px;
      }

      .hero-model {
        min-height: 0;
      }

      .stat-grid, .confusion-grid {
        grid-template-columns: 1fr;
      }
    }
"""


def _project_root_for(path: Path) -> Path:
    for candidate in (path, *path.parents):
        if candidate.name == "SR-agents":
            return candidate
    return path.parent


def _load_summary(summary_path: Path) -> dict:
    with open(summary_path, "r", encoding="utf-8") as f:
        return json.load(f)


def _load_runs_csv(summary_csv_path: Path) -> list[dict]:
    with open(summary_csv_path, "r", encoding="utf-8", newline="") as f:
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


def _humanize_policy(label_policy: str) -> str:
    if label_policy == "include_label_0_5":
        return "label 0.5 treated as INCLUDE"
    if label_policy == "exclude_label_0_5":
        return "label 0.5 treated as EXCLUDE"
    return label_policy.replace("_", " ")


def _short_review_label(review_key: str) -> str:
    return review_key.replace("_", " ")


def _format_run_label(review_key: str, run_index: int) -> str:
    return f"{review_key} run {run_index}".replace("_", " ")


def _metric_sd(values: list[float]) -> float:
    if len(values) <= 1:
        return 0.0
    return pstdev(values)


def _display_gatekeeper_model(label: str) -> str:
    normalized = str(label).strip()
    if not normalized:
        return normalized
    if "[" in normalized and normalized.endswith("]"):
        prefix, bracket_part = normalized.rsplit("[", 1)
        bracket_value = bracket_part[:-1].strip()
        if bracket_value:
            return bracket_value
        return prefix.strip()
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


def _gatekeeper_model_summary(leaderboard_rows: list[dict], runs: list[dict]) -> dict | None:
    preset_keys = _unique_in_order(
        [str(row.get("gatekeeper_preset", "")) for row in leaderboard_rows]
        + [str(run.get("gatekeeper_preset", "")) for run in runs]
    )
    labels: list[str] = []
    for preset_key in preset_keys:
        try:
            labels.append(_report_gatekeeper_name_from_preset(preset_key))
        except ValueError:
            continue
    if not labels:
        labels = _unique_in_order(
            [str(row.get("gatekeeper_model_label", "")) for row in leaderboard_rows]
            + [str(run.get("gatekeeper_model_label", "")) for run in runs]
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


def _top_metric_names(metrics: dict[str, float], count: int = 2) -> list[str]:
    ordered = sorted(metrics.items(), key=lambda item: item[1], reverse=True)
    return [name for name, _ in ordered[:count]]


def _build_study_mistakes(runs: list[dict]) -> list[dict]:
    grouped: dict[tuple[str, int], dict] = {}
    for run in runs:
        if not _as_bool(run.get("scored_for_aggregate")):
            continue
        inspection_path = Path(run.get("screening_inspection_json", ""))
        if not inspection_path.exists():
            continue
        payload = json.loads(inspection_path.read_text(encoding="utf-8"))
        for study in payload.get("studies", []):
            predicted = str(study.get("predicted_decision") or "").strip().upper()
            gold = str(study.get("gold_screening_decision") or "").strip().upper()
            if not predicted or predicted == gold:
                continue
            review_key = str(run.get("review_key", ""))
            study_index = _as_int(study.get("study_index"))
            key = (review_key, study_index)
            entry = grouped.setdefault(key, {
                "ref": f"{_short_review_label(review_key)} #{study_index}",
                "review_key": review_key,
                "review_label": _short_review_label(review_key),
                "study_index": study_index,
                "title": study.get("study_title") or f"Study {study_index}",
                "mistakes": 0,
                "error_types": Counter(),
                "gold": str(study.get("gold_label", "")),
                "outcome": study.get("gold_review_outcome") or "",
            })
            entry["mistakes"] += 1
            if gold == "INCLUDE" and predicted == "EXCLUDE":
                entry["error_types"]["false_negative"] += 1
            elif gold == "EXCLUDE" and predicted == "INCLUDE":
                entry["error_types"]["false_positive"] += 1
            else:
                entry["error_types"]["mixed"] += 1

    results = []
    for entry in grouped.values():
        if not entry["error_types"]:
            continue
        top_error = entry["error_types"].most_common(1)[0][0]
        results.append({
            "ref": entry["ref"],
            "title": entry["title"],
            "mistakes": entry["mistakes"],
            "error": top_error,
            "gold": entry["gold"],
            "outcome": entry["outcome"],
            "review_key": entry["review_key"],
        })

    return sorted(
        results,
        key=lambda item: (-item["mistakes"], item["review_key"], item["ref"]),
    )[:10]


def _narrative_run_health(overall: dict) -> str:
    metrics = {
        "accuracy": overall["macroAccuracy"],
        "precision": overall["macroPrecision"],
        "recall": overall["macroRecall"],
        "specificity": overall["macroSpecificity"],
        "F1": overall["macroF1"],
    }
    strongest = _top_metric_names(metrics, count=2)
    weakest = min(metrics.items(), key=lambda item: item[1])[0]
    scored = overall["runsScored"]
    total = overall["runsTotal"]
    incomplete = overall["runsIncomplete"]
    opening = (
        f"The bundle scored {scored} of {total} attempted runs under this policy."
        if incomplete
        else f"All {total} attempted runs were scored under this policy."
    )
    if incomplete:
        opening += f" {incomplete} run{' was' if incomplete == 1 else 's were'} excluded from scoring due to incomplete screening output."
    strongest_text = " and ".join(strongest)
    return (
        f"{opening} The strongest pooled macro metrics are {strongest_text}, "
        f"while {weakest} is the lowest of the scored-run means."
    )


def _narrative_review_performance(reviews: list[dict]) -> str:
    if not reviews:
        return "Review-level metrics become informative once scored runs are available."
    best = max(reviews, key=lambda item: item["f1"])
    worst = min(reviews, key=lambda item: item["f1"])
    return (
        f"Review difficulty varies across the bundle. "
        f"{best['label']} has the strongest mean F1, while {worst['label']} is the hardest case under this policy."
    )


def _narrative_variability(all_runs: list[dict], scored_runs: list[dict]) -> str:
    if not scored_runs:
        return "No scored runs are available yet for repeat-stability analysis."
    per_review_f1: dict[str, list[float]] = defaultdict(list)
    for run in scored_runs:
        per_review_f1[str(run.get("review_key", ""))].append(_as_float(run.get("f1")))
    widest_review = max(
        per_review_f1.items(),
        key=lambda item: _metric_sd(item[1]),
    )[0]
    incomplete_count = sum(
        1 for run in all_runs if str(run.get("run_status", "")) == "incomplete"
    )
    sentence = (
        f"Most reviews are stable across repeats. The largest run-to-run F1 spread appears in "
        f"{_short_review_label(widest_review)}."
    )
    if incomplete_count:
        sentence += f" The bundle also contains {incomplete_count} incomplete run{'s' if incomplete_count != 1 else ''}."
    return sentence


def _narrative_study_mistakes(studies: list[dict]) -> str:
    if not studies:
        return (
            "No recurring study-level mistakes were detected across the scored runs in this policy view."
        )
    error_counts = Counter(study["error"] for study in studies)
    dominant_error = error_counts.most_common(1)[0][0].replace("_", " ")
    review_counts = Counter(study["review_key"] for study in studies)
    top_reviews = ", ".join(
        _short_review_label(review_key)
        for review_key, _ in review_counts.most_common(3)
    )
    return (
        f"These titles were misclassified repeatedly across scored runs. "
        f"Most recurring mistakes are {dominant_error}s, concentrated in {top_reviews}."
    )


def _display_path(path: Path) -> str:
    project_root = _project_root_for(path.resolve())
    try:
        relative = path.resolve().relative_to(project_root)
        return str(Path("/SR-agents") / relative)
    except ValueError:
        return str(path)


def _build_report_payload(policy_dir: Path) -> dict:
    summary_payload = _load_summary(policy_dir / "summary.json")
    runs = _load_runs_csv(policy_dir / "summary.csv")
    scored_runs = [run for run in runs if _as_bool(run.get("scored_for_aggregate"))]
    leaderboard_rows = summary_payload.get("leaderboard", [])
    review_rows = sorted(
        summary_payload.get("review_leaderboard", []),
        key=lambda row: (_as_int(row.get("n_studies")), str(row.get("review_key", ""))),
    )

    overall_leaderboard = leaderboard_rows[0] if leaderboard_rows else {}
    confusion = {
        "tp": sum(_as_int(run.get("tp")) for run in scored_runs),
        "fp": sum(_as_int(run.get("fp")) for run in scored_runs),
        "tn": sum(_as_int(run.get("tn")) for run in scored_runs),
        "fn": sum(_as_int(run.get("fn")) for run in scored_runs),
    }
    total_scored_studies = sum(_as_int(run.get("n_studies")) for run in scored_runs)
    total_scored_decisions = sum(_as_int(run.get("screening_decision_count")) for run in scored_runs)
    decision_coverage = (
        total_scored_decisions / total_scored_studies if total_scored_studies else 0.0
    )

    duration_values = [_as_float(run.get("duration_seconds")) for run in scored_runs]
    metric_values = {
        "accuracy": [_as_float(run.get("accuracy")) for run in scored_runs],
        "precision": [_as_float(run.get("precision")) for run in scored_runs],
        "recall": [_as_float(run.get("recall")) for run in scored_runs],
        "specificity": [_as_float(run.get("specificity")) for run in scored_runs],
        "f1": [_as_float(run.get("f1")) for run in scored_runs],
    }
    dispersion = {
        "accuracy": _metric_sd(metric_values["accuracy"]),
        "precision": _metric_sd(metric_values["precision"]),
        "recall": _metric_sd(metric_values["recall"]),
        "specificity": _metric_sd(metric_values["specificity"]),
        "f1": _metric_sd(metric_values["f1"]),
        "duration": _metric_sd(duration_values),
    }

    reviews = []
    for row in review_rows:
        review_key = str(row.get("review_key", ""))
        reviews.append({
            "key": review_key,
            "label": _short_review_label(review_key),
            "studies": _as_int(row.get("n_studies")),
            "goldInclude": _as_int(row.get("gold_pass_count")),
            "accuracy": _as_float(row.get("mean_accuracy")),
            "precision": _as_float(row.get("mean_precision")),
            "recall": _as_float(row.get("mean_recall")),
            "specificity": _as_float(row.get("mean_specificity")),
            "f1": _as_float(row.get("mean_f1")),
            "duration": _as_float(row.get("mean_duration_seconds")),
        })

    worst_runs = []
    for run in sorted(scored_runs, key=lambda item: (_as_float(item.get("f1")), str(item.get("benchmark_run_id", ""))))[:5]:
        worst_runs.append({
            "run": _format_run_label(str(run.get("review_key", "")), _as_int(run.get("run_index"), 0)),
            "review": _short_review_label(str(run.get("review_key", ""))),
            "accuracy": _as_float(run.get("accuracy")),
            "precision": _as_float(run.get("precision")),
            "recall": _as_float(run.get("recall")),
            "f1": _as_float(run.get("f1")),
        })

    studies = _build_study_mistakes(runs)

    experiment_name = policy_dir.parent.name
    label_policy = str(summary_payload.get("gold_label_policy", policy_dir.name))
    human_policy = _humanize_policy(label_policy)
    report_title = "Title and Abstract Screening Benchmark Summary"

    badge_counts = {
        "reviews": len(summary_payload.get("review_keys", [])),
        "attempted": len(runs),
        "scored": len(scored_runs),
        "incomplete": sum(1 for run in runs if str(run.get("run_status", "")) == "incomplete"),
    }

    links = []
    for filename, label in (
        ("summary.csv", "summary.csv"),
        ("summary.json", "summary.json"),
    ):
        if (policy_dir / filename).exists():
            links.append({"href": f"./{filename}", "label": label})

    overall = {
        "runsTotal": len(runs),
        "runsScored": len(scored_runs),
        "runsCompleted": sum(1 for run in runs if str(run.get("run_status", "")) == "completed"),
        "runsIncomplete": sum(1 for run in runs if str(run.get("run_status", "")) == "incomplete"),
        "parseSuccessRate": (
            sum(1 for run in runs if _as_bool(run.get("parse_success"))) / len(runs)
            if runs else 0.0
        ),
        "decisionCoverage": decision_coverage,
        "macroAccuracy": _as_float(overall_leaderboard.get("mean_accuracy")),
        "macroPrecision": _as_float(overall_leaderboard.get("mean_precision")),
        "macroRecall": _as_float(overall_leaderboard.get("mean_recall")),
        "macroSpecificity": _as_float(overall_leaderboard.get("mean_specificity")),
        "macroF1": _as_float(overall_leaderboard.get("mean_f1")),
        "meanDurationSeconds": _as_float(overall_leaderboard.get("mean_duration_seconds")),
        "durationStdSeconds": dispersion["duration"],
        "confusion": confusion,
        "dispersion": dispersion,
    }
    model_summary = _gatekeeper_model_summary(leaderboard_rows, runs)

    return {
        "meta": {
            "title": report_title,
            "title_html": "Title and Abstract<br>Screening Benchmark<br>Summary",
            "eyebrow": f"Policy-scored benchmark summary • {human_policy}",
            "eyebrow_code": label_policy,
            "experiment_name": experiment_name,
            "policy_path": _display_path(policy_dir),
            "badges": badge_counts,
            "links": links,
            "gatekeeper_model": model_summary,
            "run_health_paragraph": _narrative_run_health(overall),
            "review_paragraph": _narrative_review_performance(reviews),
            "variability_paragraph": _narrative_variability(runs, scored_runs),
            "study_paragraph": _narrative_study_mistakes(studies),
        },
        "overall": overall,
        "reviews": reviews,
        "worstRuns": worst_runs,
        "studies": studies,
    }


def _render_links(links: list[dict]) -> str:
    return "\n".join(
        f'            <a href="{html.escape(link["href"])}">{html.escape(link["label"])}</a>'
        for link in links
    )


def _report_html(payload: dict) -> str:
    meta = payload["meta"]
    benchmark_json = json.dumps({
        "overall": payload["overall"],
        "reviews": payload["reviews"],
        "worstRuns": payload["worstRuns"],
        "studies": payload["studies"],
    }, ensure_ascii=False, indent=2)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{html.escape(meta["title"])}</title>
  <style>
{_REPORT_CSS}
  </style>
</head>
<body>
  <main class="page">
    <header class="hero">
      <div class="eyebrow">{html.escape(meta["eyebrow"])} • <code>{html.escape(meta["eyebrow_code"])}</code></div>
      <div class="hero-grid">
        <div class="hero-copy">
          <h1>{meta["title_html"]}</h1>
          <p>
            This page summarizes the measured screening performance for the benchmark bundle in
            <code>{html.escape(meta["experiment_name"])}</code> under the active gold-label
            policy. It focuses on run health, aggregate metrics, review-level behavior, runtime,
            repeat stability, and recurring study-level errors across scored runs.
          </p>
          <div class="badge-row">
            <span class="badge">{meta["badges"]["reviews"]} reviews</span>
            <span class="badge">{meta["badges"]["attempted"]} attempted runs</span>
            <span class="badge">{meta["badges"]["scored"]} scored runs</span>
            <span class="badge">{meta["badges"]["incomplete"]} incomplete run{"s" if meta["badges"]["incomplete"] != 1 else ""}</span>
          </div>
          <div class="link-row">
{_render_links(meta["links"])}
          </div>
        </div>
        <div class="hero-side">
          {f'''<div class="hero-model"><div class="k">{html.escape(meta["gatekeeper_model"]["label"])}</div><div class="v">{html.escape(meta["gatekeeper_model"]["value"])}</div></div>''' if meta.get("gatekeeper_model") else ""}
          <div class="stat-grid" id="hero-stats"></div>
        </div>
      </div>
    </header>

    <section class="section">
      <div class="section-header">
        <div>
          <h2>Run health and aggregate metrics</h2>
        </div>
        <p>
          {html.escape(meta["run_health_paragraph"])}
        </p>
      </div>
      <div class="grid-2">
        <div class="panel">
          <h3>Macro metrics across scored runs</h3>
          <p>Mean values are computed from scored runs only.</p>
          <div class="mini-grid" id="macro-grid"></div>
        </div>
        <div class="panel">
          <h3>Pooled confusion totals</h3>
          <p>Counts aggregated across all study decisions in scored runs.</p>
          <div class="confusion-grid" id="confusion-grid"></div>
        </div>
      </div>
    </section>

    <section class="section">
      <div class="section-header">
        <div>
          <h2>Performance by review</h2>
        </div>
        <p>
          {html.escape(meta["review_paragraph"])}
        </p>
      </div>
      <div class="grid-2">
        <div class="panel">
          <h3>F1 and recall by review</h3>
          <p>Each review is shown with its mean scored-run F1 and recall.</p>
          <div id="review-chart" class="chart"></div>
        </div>
        <div class="panel">
          <h3>Mean runtime by review</h3>
          <p>Runtime is shown as the mean scored-run duration for each review.</p>
          <div id="runtime-chart" class="chart"></div>
        </div>
      </div>
      <div class="panel" style="margin-top:18px;">
        <table>
          <thead>
            <tr>
              <th>Review</th>
              <th>Studies</th>
              <th>Gold include</th>
              <th>Accuracy</th>
              <th>Precision</th>
              <th>Recall</th>
              <th>Specificity</th>
              <th>F1</th>
              <th>Mean runtime</th>
            </tr>
          </thead>
          <tbody id="review-table"></tbody>
        </table>
      </div>
    </section>

    <section class="section">
      <div class="section-header">
        <div>
          <h2>Run variability</h2>
        </div>
        <p>
          {html.escape(meta["variability_paragraph"])}
        </p>
      </div>
      <div class="grid-2">
        <div class="panel">
          <h3>Metric standard deviation across scored runs</h3>
          <p>Lower values indicate more repeat-to-repeat stability across the scored runs.</p>
          <div class="mini-grid" id="dispersion-grid"></div>
        </div>
        <div class="panel">
          <h3>Lowest-F1 scored runs</h3>
          <p>These runs define the lower tail of the benchmark under this policy.</p>
          <table class="compact-table">
            <thead>
              <tr>
                <th>Run</th>
                <th class="numeric">Accuracy</th>
                <th class="numeric">Precision</th>
                <th class="numeric">Recall</th>
                <th class="numeric">F1</th>
              </tr>
            </thead>
            <tbody id="worst-runs"></tbody>
          </table>
        </div>
      </div>
    </section>

    <section class="section">
      <div class="section-header">
        <div>
          <h2>Recurring study-level mistakes</h2>
        </div>
        <p>
          {html.escape(meta["study_paragraph"])}
        </p>
      </div>
      <div class="study-list" id="study-list"></div>
      <p class="footer-note">
        Study-level entries below are ordered by repeated mistake count across scored runs.
      </p>
    </section>
  </main>

  <script>
    const benchmark = {benchmark_json};

    const fmtPct = value => `${{(value * 100).toFixed(1)}}%`;
    const fmtPctShort = value => `${{(value * 100).toFixed(0)}}%`;
    const fmtNum = value => Number(value).toLocaleString();
    const fmtSec = value => `${{Math.round(value)}}s`;

    function mountHeroStats() {{
      const stats = [
        {{
          label: "Macro F1",
          value: fmtPct(benchmark.overall.macroF1),
          note: `Mean F1 across the ${{benchmark.overall.runsScored}} scored runs.`
        }},
        {{
          label: "Macro recall",
          value: fmtPct(benchmark.overall.macroRecall),
          note: "Mean recall across scored runs."
        }},
        {{
          label: "Decision coverage",
          value: fmtPct(benchmark.overall.decisionCoverage),
          note: "Coverage across all scored study decisions."
        }},
        {{
          label: "Mean runtime",
          value: fmtSec(benchmark.overall.meanDurationSeconds),
          note: `Scored-run standard deviation ${{fmtSec(benchmark.overall.durationStdSeconds)}}.`
        }}
      ];

      document.getElementById("hero-stats").innerHTML = stats.map(stat => `
        <div class="stat">
          <div class="label">${{stat.label}}</div>
          <div class="value">${{stat.value}}</div>
          <div class="note">${{stat.note}}</div>
        </div>
      `).join("");
    }}

    function mountMacroGrid() {{
      const metrics = [
        ["Accuracy", benchmark.overall.macroAccuracy],
        ["Precision", benchmark.overall.macroPrecision],
        ["Recall", benchmark.overall.macroRecall],
        ["Specificity", benchmark.overall.macroSpecificity],
        ["F1", benchmark.overall.macroF1],
        ["Parse success", benchmark.overall.parseSuccessRate]
      ];
      document.getElementById("macro-grid").innerHTML = metrics.map(([k, v]) => `
        <div class="chip">
          <div class="k">${{k}}</div>
          <div class="v">${{fmtPct(v)}}</div>
        </div>
      `).join("");
    }}

    function mountConfusionGrid() {{
      const total = Object.values(benchmark.overall.confusion).reduce((sum, value) => sum + value, 0);
      const cells = [
        {{ label: "True positive", value: benchmark.overall.confusion.tp, bg: "var(--good)" }},
        {{ label: "False negative", value: benchmark.overall.confusion.fn, bg: "var(--accent-2)" }},
        {{ label: "False positive", value: benchmark.overall.confusion.fp, bg: "var(--accent-3)", light: true }},
        {{ label: "True negative", value: benchmark.overall.confusion.tn, bg: "var(--accent)" }}
      ];
      document.getElementById("confusion-grid").innerHTML = cells.map(cell => `
        <div class="confusion-cell ${{cell.light ? "light" : ""}}" style="background:${{cell.bg}}">
          <div class="cell-label">${{cell.label}}</div>
          <div class="cell-value">${{fmtNum(cell.value)}}</div>
          <div class="cell-note">${{fmtPctShort(cell.value / total)}} of pooled study decisions</div>
        </div>
      `).join("");
    }}

    function renderBarChart(mountId, valueKey, colorA, colorB, labelA, labelB) {{
      const mount = document.getElementById(mountId);
      const width = mount.clientWidth || 520;
      const estimateLabelWidth = text => Math.max(56, text.length * 8 + 16);
      const rightLabelReserve = Math.max(
        ...benchmark.reviews.flatMap(review => [
          estimateLabelWidth(fmtPct(review[valueKey])),
          estimateLabelWidth(fmtPct(review[labelB]))
        ])
      );
      const margin = {{ top: 24, right: rightLabelReserve, bottom: 42, left: 170 }};
      const rowHeight = 58;
      const innerWidth = width - margin.left - margin.right;
      const height = margin.top + margin.bottom + rowHeight * benchmark.reviews.length;
      const rows = benchmark.reviews.map((review, i) => {{
        const y = margin.top + rowHeight * i + 10;
        const barWidth = innerWidth * review[valueKey];
        return `
          <text x="${{margin.left - 12}}" y="${{y + 16}}" text-anchor="end" fill="#667084" font-size="13">${{review.label}}</text>
          <rect x="${{margin.left}}" y="${{y}}" width="${{barWidth}}" height="14" rx="7" fill="${{colorA}}"></rect>
          <rect x="${{margin.left}}" y="${{y + 20}}" width="${{innerWidth * review[labelB]}}" height="14" rx="7" fill="${{colorB}}"></rect>
          <text x="${{margin.left + barWidth + 8}}" y="${{y + 12}}" fill="${{colorA}}" font-size="12" font-weight="700">${{fmtPct(review[valueKey])}}</text>
          <text x="${{margin.left + innerWidth * review[labelB] + 8}}" y="${{y + 32}}" fill="${{colorB}}" font-size="12" font-weight="700">${{fmtPct(review[labelB])}}</text>
        `;
      }}).join("");

      const ticks = [0, 0.25, 0.5, 0.75, 1.0].map(value => {{
        const x = margin.left + innerWidth * value;
        return `
          <line x1="${{x}}" y1="${{margin.top - 8}}" x2="${{x}}" y2="${{height - margin.bottom + 8}}" stroke="rgba(30,36,48,0.1)" stroke-width="1"></line>
          <text x="${{x}}" y="${{height - 12}}" text-anchor="middle" fill="#667084" font-size="12">${{fmtPctShort(value)}}</text>
        `;
      }}).join("");

      mount.innerHTML = `
        <svg viewBox="0 0 ${{width}} ${{height}}" width="100%" height="${{height}}">
          ${{ticks}}
          ${{rows}}
          <text x="${{margin.left}}" y="14" fill="${{colorA}}" font-size="12" font-weight="700">${{labelA}}</text>
          <text x="${{margin.left + 92}}" y="14" fill="${{colorB}}" font-size="12" font-weight="700">${{labelB}}</text>
        </svg>
      `;
    }}

    function renderRuntimeChart() {{
      const mount = document.getElementById("runtime-chart");
      const width = mount.clientWidth || 520;
      const estimateLabelWidth = text => Math.max(56, text.length * 8 + 16);
      const rightLabelReserve = Math.max(
        ...benchmark.reviews.map(review => estimateLabelWidth(fmtSec(review.duration)))
      );
      const margin = {{ top: 24, right: rightLabelReserve, bottom: 42, left: 170 }};
      const innerWidth = width - margin.left - margin.right;
      const rowHeight = 52;
      const height = margin.top + margin.bottom + rowHeight * benchmark.reviews.length;
      const maxDuration = Math.max(...benchmark.reviews.map(r => r.duration), 1);

      const rows = benchmark.reviews.map((review, i) => {{
        const y = margin.top + rowHeight * i + 12;
        const w = innerWidth * (review.duration / maxDuration);
        return `
          <text x="${{margin.left - 12}}" y="${{y + 14}}" text-anchor="end" fill="#667084" font-size="13">${{review.label}}</text>
          <rect x="${{margin.left}}" y="${{y}}" width="${{w}}" height="16" rx="8" fill="var(--accent)"></rect>
          <text x="${{margin.left + w + 8}}" y="${{y + 13}}" fill="var(--accent)" font-size="12" font-weight="700">${{fmtSec(review.duration)}}</text>
        `;
      }}).join("");

      mount.innerHTML = `
        <svg viewBox="0 0 ${{width}} ${{height}}" width="100%" height="${{height}}">
          ${{rows}}
        </svg>
      `;
    }}

    function mountReviewTable() {{
      document.getElementById("review-table").innerHTML = benchmark.reviews.map(review => `
        <tr>
          <td><strong>${{review.label}}</strong></td>
          <td>${{review.studies}}</td>
          <td>${{review.goldInclude}}</td>
          <td>${{fmtPct(review.accuracy)}}</td>
          <td>${{fmtPct(review.precision)}}</td>
          <td>${{fmtPct(review.recall)}}</td>
          <td>${{fmtPct(review.specificity)}}</td>
          <td>${{fmtPct(review.f1)}}</td>
          <td>${{fmtSec(review.duration)}}</td>
        </tr>
      `).join("");
    }}

    function mountDispersionGrid() {{
      const items = [
        ["Accuracy SD", benchmark.overall.dispersion.accuracy],
        ["Precision SD", benchmark.overall.dispersion.precision],
        ["Recall SD", benchmark.overall.dispersion.recall],
        ["Specificity SD", benchmark.overall.dispersion.specificity],
        ["F1 SD", benchmark.overall.dispersion.f1],
        ["Runtime SD", benchmark.overall.dispersion.duration, true]
      ];
      document.getElementById("dispersion-grid").innerHTML = items.map(([k, value, isDuration]) => `
        <div class="chip">
          <div class="k">${{k}}</div>
          <div class="v">${{isDuration ? fmtSec(value) : fmtPct(value)}}</div>
        </div>
      `).join("");
    }}

    function mountWorstRuns() {{
      document.getElementById("worst-runs").innerHTML = benchmark.worstRuns.map(run => `
        <tr>
          <td class="run-label">${{run.run}}<small>${{run.review}}</small></td>
          <td class="numeric">${{fmtPct(run.accuracy)}}</td>
          <td class="numeric">${{fmtPct(run.precision)}}</td>
          <td class="numeric">${{fmtPct(run.recall)}}</td>
          <td class="numeric">${{fmtPct(run.f1)}}</td>
        </tr>
      `).join("");
    }}

    function mountStudies() {{
      const mount = document.getElementById("study-list");
      if (!benchmark.studies.length) {{
        mount.innerHTML = `<div class="panel"><p>No recurring study-level mistakes were found in the scored runs for this policy.</p></div>`;
        return;
      }}
      mount.innerHTML = benchmark.studies.map(study => `
        <div class="study-item">
          <div class="study-head">
            <div class="study-ref">${{study.ref}}</div>
            <div class="study-count">${{study.mistakes}} repeated mistakes</div>
          </div>
          <div class="study-title">${{study.title}}</div>
          <div class="pill-row">
            <span class="pill">${{study.error.replaceAll("_", " ")}}</span>
            <span class="pill">gold ${{study.gold}}</span>
            <span class="pill">${{study.outcome}}</span>
          </div>
        </div>
      `).join("");
    }}

    mountHeroStats();
    mountMacroGrid();
    mountConfusionGrid();
    renderBarChart("review-chart", "f1", "var(--accent)", "var(--good)", "F1", "recall");
    renderRuntimeChart();
    mountReviewTable();
    mountDispersionGrid();
    mountWorstRuns();
    mountStudies();
  </script>
</body>
</html>
"""


def write_policy_html_report(policy_dir: Path) -> dict:
    payload = _build_report_payload(policy_dir)
    report_path = policy_dir / HTML_REPORT_FILENAME
    report_path.write_text(_report_html(payload), encoding="utf-8")
    return {
        "report_path": str(report_path),
        "title": payload["meta"]["title"],
    }


def write_html_reports(target_dir: Path) -> list[dict]:
    target_dir = Path(target_dir)

    if (target_dir / "summary.json").exists() and (target_dir / "runs").exists():
        return [write_policy_html_report(target_dir)]

    policy_dirs = [
        child
        for child in target_dir.iterdir()
        if child.is_dir()
        and (child / "summary.json").exists()
        and (child / "runs").exists()
    ] if target_dir.exists() else []

    if not policy_dirs:
        raise FileNotFoundError(
            f"No policy folder or experiment folder with policy subdirectories found at: {target_dir}"
        )

    results = [write_policy_html_report(policy_dir) for policy_dir in sorted(policy_dirs)]
    policy_names = {policy_dir.name for policy_dir in policy_dirs}
    if {"include_policy", "exclude_policy"}.issubset(policy_names):
        results.append(write_policy_comparison_report(target_dir))
    return results
