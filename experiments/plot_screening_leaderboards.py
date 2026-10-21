"""Render charts for screening benchmark markdown leaderboards.

Reads totals and per-review markdown tables produced by the benchmark
harness, parses gatekeeper model scores, and writes horizontal bar charts
(single-panel and faceted) for slides and reports.
"""

from __future__ import annotations

import argparse
import csv
import io
import re
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


METRICS = ("F1", "Recall", "Precision", "Accuracy")
MODEL_PATTERN = re.compile(r"^(.*?)\s*\[(.*?)\]\s*$")
REVIEW_HEADER_PATTERN = re.compile(r"^##\s+(.+?)\s*$")


def _clean_model_name(raw_name: str) -> str:
    match = MODEL_PATTERN.match(raw_name.strip())
    if not match:
        return raw_name.strip()
    _, display_name = match.groups()
    return display_name.strip()


def _parse_markdown_table(table_lines: list[str]) -> list[dict[str, str]]:
    rows = []
    reader = csv.reader(io.StringIO("\n".join(table_lines)), delimiter="|")
    parsed_rows = [row for row in reader if row]
    if len(parsed_rows) < 3:
        return rows

    header = [cell.strip() for cell in parsed_rows[0][1:-1]]
    for row in parsed_rows[2:]:
        cells = [cell.strip() for cell in row[1:-1]]
        if len(cells) != len(header):
            continue
        rows.append(dict(zip(header, cells, strict=False)))
    return rows


# Markdown table parsing


def parse_totals_leaderboard(path: Path) -> list[dict[str, object]]:
    lines = path.read_text(encoding="utf-8").splitlines()
    table_lines = [line for line in lines if line.strip().startswith("|")]
    rows = _parse_markdown_table(table_lines)
    parsed_rows = []
    for row in rows:
        parsed = {"Model": _clean_model_name(row["Gatekeeper Model"])}
        for metric in METRICS:
            parsed[metric] = float(row[metric])
        parsed_rows.append(parsed)
    parsed_rows.sort(key=lambda item: item["F1"], reverse=True)
    return parsed_rows


def parse_review_leaderboard(path: Path) -> dict[str, list[dict[str, object]]]:
    lines = path.read_text(encoding="utf-8").splitlines()
    review_rows: dict[str, list[dict[str, object]]] = {}
    current_review: str | None = None
    current_table: list[str] = []

    def flush_current_table() -> None:
        nonlocal current_table
        if not current_review or not current_table:
            current_table = []
            return
        rows = _parse_markdown_table(current_table)
        parsed_rows = []
        for row in rows:
            parsed = {"Model": _clean_model_name(row["Gatekeeper Model"])}
            for metric in METRICS:
                parsed[metric] = float(row[metric])
            parsed_rows.append(parsed)
        review_rows[current_review] = parsed_rows
        current_table = []

    for line in lines:
        review_match = REVIEW_HEADER_PATTERN.match(line)
        if review_match:
            flush_current_table()
            current_review = review_match.group(1)
            continue
        if line.strip().startswith("|"):
            current_table.append(line)
        elif current_table:
            flush_current_table()

    flush_current_table()
    return review_rows


def _metric_color(metric: str) -> str:
    palette = {
        "F1": "#1b9e77",
        "Recall": "#d95f02",
        "Precision": "#c44e52",
        "Accuracy": "#4c78a8",
    }
    return palette[metric]


def _style_legend(legend: plt.Legend | None) -> None:
    if legend is None:
        return
    frame = legend.get_frame()
    frame.set_facecolor("white")
    frame.set_alpha(0.95)
    frame.set_edgecolor("#d0d7de")
    frame.set_linewidth(1.0)


def _collect_metric_handles():
    return [
        plt.Rectangle((0, 0), 1, 1, color=_metric_color(metric), label=metric)
        for metric in METRICS
    ]


# Matplotlib chart export


def plot_totals_leaderboard(rows: list[dict[str, object]], output_path: Path) -> None:
    models = [row["Model"] for row in rows]
    y_positions = np.arange(len(models))
    bar_height = 0.18
    offsets = np.linspace(-1.5 * bar_height, 1.5 * bar_height, len(METRICS))

    fig, ax = plt.subplots(figsize=(13, 6.8))
    for metric, offset in zip(METRICS, offsets, strict=False):
        values = [row[metric] for row in rows]
        ax.barh(
            y_positions + offset,
            values,
            height=bar_height,
            label=metric,
            color=_metric_color(metric),
        )

    ax.set_xlim(0, 1.02)
    ax.set_xlabel("Score")
    ax.set_ylabel("Model")
    ax.set_title("Screening Benchmark Totals Leaderboard", pad=14)
    ax.set_yticks(y_positions)
    ax.set_yticklabels(models)
    ax.invert_yaxis()
    ax.grid(axis="x", linestyle="--", alpha=0.3)
    legend = fig.legend(
        handles=_collect_metric_handles(),
        loc="upper center",
        bbox_to_anchor=(0.5, 1.0),
        ncol=4,
        frameon=True,
        fontsize=11,
        borderpad=0.6,
        handlelength=1.8,
    )
    _style_legend(legend)

    fig.tight_layout(rect=(0, 0, 1, 0.92))
    fig.savefig(output_path, dpi=200, bbox_inches="tight")
    plt.close(fig)


def plot_totals_leaderboard_vertical(
    rows: list[dict[str, object]], output_path: Path
) -> None:
    models = [row["Model"] for row in rows]
    x_positions = np.arange(len(models))
    bar_width = 0.18
    offsets = np.linspace(-1.5 * bar_width, 1.5 * bar_width, len(METRICS))

    fig, ax = plt.subplots(figsize=(13.5, 8))
    for metric, offset in zip(METRICS, offsets, strict=False):
        values = [row[metric] for row in rows]
        ax.bar(
            x_positions + offset,
            values,
            width=bar_width,
            label=metric,
            color=_metric_color(metric),
        )

    ax.set_ylim(0, 1.02)
    ax.set_ylabel("Score")
    ax.set_xlabel("Model")
    ax.set_title("Screening Benchmark Totals Leaderboard", pad=14)
    ax.set_xticks(x_positions)
    ax.set_xticklabels(models, rotation=25, ha="right")
    ax.grid(axis="y", linestyle="--", alpha=0.3)
    legend = fig.legend(
        handles=_collect_metric_handles(),
        loc="upper center",
        bbox_to_anchor=(0.5, 1.0),
        ncol=4,
        frameon=True,
        fontsize=11,
        borderpad=0.6,
        handlelength=1.8,
    )
    _style_legend(legend)

    fig.tight_layout(rect=(0, 0, 1, 0.92))
    fig.savefig(output_path, dpi=200, bbox_inches="tight")
    plt.close(fig)


def plot_review_leaderboard(
    review_rows: dict[str, list[dict[str, object]]], output_path: Path
) -> None:
    reviews = list(review_rows.keys())
    figure_rows = int(np.ceil(len(reviews) / 2))
    fig, axes = plt.subplots(
        figure_rows,
        2,
        figsize=(18, max(figure_rows * 4.6, 8)),
        constrained_layout=False,
    )
    axes_flat = np.atleast_1d(axes).flatten()
    bar_height = 0.18
    offsets = np.linspace(-1.5 * bar_height, 1.5 * bar_height, len(METRICS))

    for axis, review in zip(axes_flat, reviews, strict=False):
        rows = sorted(review_rows[review], key=lambda item: item["F1"], reverse=True)
        models = [row["Model"] for row in rows]
        y_positions = np.arange(len(models))

        for metric, offset in zip(METRICS, offsets, strict=False):
            values = [row[metric] for row in rows]
            axis.barh(
                y_positions + offset,
                values,
                height=bar_height,
                label=metric,
                color=_metric_color(metric),
            )

        axis.set_title(review)
        axis.set_xlim(0, 1.02)
        axis.set_yticks(y_positions)
        axis.set_yticklabels(models)
        axis.invert_yaxis()
        axis.grid(axis="x", linestyle="--", alpha=0.3)

    for axis in axes_flat[len(reviews):]:
        axis.axis("off")

    legend = fig.legend(
        handles=_collect_metric_handles(),
        loc="upper center",
        bbox_to_anchor=(0.5, 0.965),
        ncol=4,
        frameon=True,
        fontsize=10,
        borderpad=0.55,
        handlelength=1.6,
    )
    _style_legend(legend)
    fig.suptitle("Review-Level Screening Benchmark Leaderboard", fontsize=16, y=0.992)
    fig.tight_layout(rect=(0, 0, 1, 0.9))
    fig.savefig(output_path, dpi=200, bbox_inches="tight")
    plt.close(fig)


def plot_review_leaderboard_vertical(
    review_rows: dict[str, list[dict[str, object]]], output_path: Path
) -> None:
    reviews = list(review_rows.keys())
    figure_rows = int(np.ceil(len(reviews) / 2))
    fig, axes = plt.subplots(
        figure_rows,
        2,
        figsize=(18, max(figure_rows * 5.3, 9)),
        constrained_layout=False,
    )
    axes_flat = np.atleast_1d(axes).flatten()
    bar_width = 0.18
    offsets = np.linspace(-1.5 * bar_width, 1.5 * bar_width, len(METRICS))

    for axis, review in zip(axes_flat, reviews, strict=False):
        rows = sorted(review_rows[review], key=lambda item: item["F1"], reverse=True)
        models = [row["Model"] for row in rows]
        x_positions = np.arange(len(models))

        for metric, offset in zip(METRICS, offsets, strict=False):
            values = [row[metric] for row in rows]
            axis.bar(
                x_positions + offset,
                values,
                width=bar_width,
                label=metric,
                color=_metric_color(metric),
            )

        axis.set_title(review)
        axis.set_ylim(0, 1.02)
        axis.set_xticks(x_positions)
        axis.set_xticklabels(models, rotation=25, ha="right")
        axis.grid(axis="y", linestyle="--", alpha=0.3)

    for axis in axes_flat[len(reviews):]:
        axis.axis("off")

    legend = fig.legend(
        handles=_collect_metric_handles(),
        loc="upper center",
        bbox_to_anchor=(0.5, 0.965),
        ncol=4,
        frameon=True,
        fontsize=10,
        borderpad=0.55,
        handlelength=1.6,
    )
    _style_legend(legend)
    fig.suptitle("Review-Level Screening Benchmark Leaderboard", fontsize=16, y=0.992)
    fig.tight_layout(rect=(0, 0, 1, 0.9))
    fig.savefig(output_path, dpi=200, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--totals-markdown",
        type=Path,
        default=Path("data/experiments/output/screening_benchmarks/totals_leaderboard.md"),
    )
    parser.add_argument(
        "--review-markdown",
        type=Path,
        default=Path(
            "data/experiments/output/screening_benchmarks/totals_review_leaderboard.md"
        ),
    )
    parser.add_argument(
        "--totals-output",
        type=Path,
        default=Path(
            "data/experiments/output/screening_benchmarks/totals_leaderboard_metrics.png"
        ),
    )
    parser.add_argument(
        "--review-output",
        type=Path,
        default=Path(
            "data/experiments/output/screening_benchmarks/totals_review_leaderboard_metrics.png"
        ),
    )
    parser.add_argument(
        "--totals-output-vertical",
        type=Path,
        default=Path(
            "data/experiments/output/screening_benchmarks/totals_leaderboard_metrics_vertical.png"
        ),
    )
    parser.add_argument(
        "--review-output-vertical",
        type=Path,
        default=Path(
            "data/experiments/output/screening_benchmarks/totals_review_leaderboard_metrics_vertical.png"
        ),
    )
    args = parser.parse_args()

    totals_rows = parse_totals_leaderboard(args.totals_markdown)
    review_rows = parse_review_leaderboard(args.review_markdown)

    args.totals_output.parent.mkdir(parents=True, exist_ok=True)
    args.review_output.parent.mkdir(parents=True, exist_ok=True)
    args.totals_output_vertical.parent.mkdir(parents=True, exist_ok=True)
    args.review_output_vertical.parent.mkdir(parents=True, exist_ok=True)

    plot_totals_leaderboard(totals_rows, args.totals_output)
    plot_review_leaderboard(review_rows, args.review_output)
    plot_totals_leaderboard_vertical(totals_rows, args.totals_output_vertical)
    plot_review_leaderboard_vertical(review_rows, args.review_output_vertical)


if __name__ == "__main__":
    main()
