"""Shared Streamlit helpers: CLI args, formatting, charts, and summaries.

Bridges ``load.load_data`` with page scripts, caches the combined runs
DataFrame, and provides Plotly heatmaps and distribution plots used across
leaderboard and research-question views.
"""

import argparse
import logging
import math
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

from streamlit_app.constants import (
    EXPERIMENT_ARCHITECTURE_LABEL_TO_VALUE_INDEX,
    GOLD_LABEL_POLICY_LABEL_TO_VALUE_INDEX,
    LOGGING_LEVEL,
    MODEL_LABEL_TO_VALUE_INDEX,
)
from streamlit_app.load import load_data
from streamlit_app.utils import setup_logger

# from loader import DataDirectoryError, find_json_files, get_suites, load_json

LOGGER = logging.getLogger(__name__)

SIZE_BAND_ORDER = ['small_10', 'lower_mid_25', 'mid_50', 'upper_mid_100', 'large_100_plus']
DURATION_STEP = 900  # 15-minute ticks for the duration select_slider

DISPLAY_COLS = [
    'benchmark_architecture', 'gold_label_policy', 'suite', 'review_key',
    'size_band',
    'gatekeeper_preset',
    # 'n_runs', 'n_scored_runs', 'n_completed_runs', 'n_incomplete_runs', 'n_error_runs',
    'n_studies',
    'gold_pass_count',
    'balance',
    # 'mean_accuracy', 'mean_precision', 'mean_recall', 'mean_f1',
    'accuracy', 'precision', 'recall', 'f1',
    'total_tokens',
    'duration_seconds',
]


# CLI parsing and cached run loading


# def resolve_data_dir() -> str:
#     parser = argparse.ArgumentParser(add_help=False)
#     parser.add_argument("--benchmark-results-dir", type=str, default=None)
#     try:
#         args, _ = parser.parse_known_args(sys.argv[1:])
#     except SystemExit:
#         args = argparse.Namespace(benchmark_results_dir=None)
#     if args.benchmark_results_dir is not None:
#         return args.benchmark_results_dir
#     env_value = os.environ.get(ENV_VAR_NAME)
#     if env_value is not None:
#         return env_value
#     return DEFAULT_BENCHMARK_RESULTS_DIR


def parse_cli_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument(
        'benchmark_results_dir',
        type=str,
        help='Must be the first argument passed after `--` — placing it after a `nargs=\'+\'` option '
             '(e.g. `--models`) would cause it to be swallowed as one of that option\'s values.',
    )
    parser.add_argument(
        '--architectures',
        choices=list(EXPERIMENT_ARCHITECTURE_LABEL_TO_VALUE_INDEX.keys()),
        nargs='+',
    )
    parser.add_argument(
        '--gold-label-policies',
        choices=list(GOLD_LABEL_POLICY_LABEL_TO_VALUE_INDEX.keys()),
        nargs='+',
    )
    parser.add_argument(
        '--logging-level',
        choices=list(range(len(LOGGING_LEVEL))),
        type=int,
        default=LOGGING_LEVEL.index(logging.INFO),
    )
    parser.add_argument(
        '--models',
        choices=list(MODEL_LABEL_TO_VALUE_INDEX.keys()),
        nargs='+',
        help='Explicit definition of models for which to collect the performed runs results. If used, only runs of '
             'models defined with this argument will be collected, excluding the runs ran with models potentially '
             'defined with `--ignore-models`.'
    )
    parser.add_argument(
        '--ignore-models',
        choices=list(MODEL_LABEL_TO_VALUE_INDEX.keys()),
        nargs='+',
        help='Definition of models for which to ignore the respective runs.'
    )
    parser.add_argument(
        '--keep-all',
        action='store_true',
        help='Keep runs that were not completed or which may have raised an error. By default these are '
             'filtered out.'
    )
    args = parser.parse_args(sys.argv[1:])
    return args


def get_new_runs() -> pd.DataFrame:
    """Parse CLI args and return the cached DataFrame from the new `load.load_data` loader."""
    cli_args = parse_cli_args()
    setup_logger(LOGGER, LOGGING_LEVEL[cli_args.logging_level])

    architectures = set(
        EXPERIMENT_ARCHITECTURE_LABEL_TO_VALUE_INDEX[a] for a in cli_args.architectures
    ) if cli_args.architectures else set()
    gold_label_policies = set(
        GOLD_LABEL_POLICY_LABEL_TO_VALUE_INDEX[p] for p in cli_args.gold_label_policies
    ) if cli_args.gold_label_policies else set()

    explicit_models = set(cli_args.models) if cli_args.models else set(MODEL_LABEL_TO_VALUE_INDEX.keys())
    ignore_models = set(cli_args.ignore_models) if cli_args.ignore_models else set()
    models = explicit_models - ignore_models

    benchmark_results_dir = Path(os.path.expandvars(cli_args.benchmark_results_dir)).expanduser().resolve().absolute()

    return load_data(
        benchmark_results_dir,
        architectures=architectures,
        gold_label_policies=gold_label_policies,
        models=models,
        keep_completed=not cli_args.keep_all,
    )


# Human-readable metric formatting


def fmt_tokens(n: float) -> str:
    for threshold, suffix in [(1e12, 'T'), (1e9, 'G'), (1e6, 'M'), (1e3, 'K')]:
        if n >= threshold:
            return f"{n / threshold:.2f}{suffix}"
    return f"{n:.0f}"


def fmt_duration(seconds) -> str:
    s = int(seconds)
    h, rem = divmod(s, 3600)
    m, sec = divmod(rem, 60)
    return f"{h:02d}:{m:02d}:{sec:02d}"


def parse_duration(hms: str) -> int:
    h, m, s = map(int, hms.split(':'))
    return h * 3600 + m * 60 + s


def between_or_nan(series: pd.Series, lo, hi) -> pd.Series:
    return series.isna() | series.between(lo, hi)


# @st.cache_data
# def load_all_data(files: tuple[str, ...]) -> pd.DataFrame:
#     df = pd.concat([load_json(f) for f in files], ignore_index=True)
#     df['balance'] = df['gold_pass_count'] / df['n_studies']
#     return df


# def get_runs() -> pd.DataFrame:
#     """Resolve data directory, find JSON files, and return the cached DataFrame."""
#     data_dir = resolve_data_dir()
#     json_files = find_json_files(data_dir)
#     return load_all_data(tuple(json_files))


# Coverage heatmaps (run counts per review × model)


_HEATMAP_ZERO_COLOR = '#c0392b'
_HEATMAP_DARK_GREEN = '#0b3d1f'
_HEATMAP_LIGHT_GREEN = '#c8f0d8'


def _lerp_hex(c1: str, c2: str, t: float) -> str:
    r1, g1, b1 = int(c1[1:3], 16), int(c1[3:5], 16), int(c1[5:7], 16)
    r2, g2, b2 = int(c2[1:3], 16), int(c2[3:5], 16), int(c2[5:7], 16)
    r = round(r1 + (r2 - r1) * t)
    g = round(g1 + (g2 - g1) * t)
    b = round(b1 + (b2 - b1) * t)
    return f'#{r:02x}{g:02x}{b:02x}'


def make_colorscale(z_max: int) -> list:
    """Quantized step colorscale for non-negative integer values 0..z_max: 0 is red,
    1..z_max are greens running from dark (1) to light (z_max)."""
    if z_max <= 0:
        return [[0.0, _HEATMAP_ZERO_COLOR], [1.0, _HEATMAP_ZERO_COLOR]]

    greens = [
        _lerp_hex(_HEATMAP_DARK_GREEN, _HEATMAP_LIGHT_GREEN, i / (z_max - 1) if z_max > 1 else 0.0)
        for i in range(z_max)
    ]
    colors = [_HEATMAP_ZERO_COLOR] + greens

    n_bands = z_max + 1
    colorscale = []
    for i, color in enumerate(colors):
        colorscale.append([i / n_bands, color])
        colorscale.append([(i + 1) / n_bands, color])
    return colorscale


def render_heatmap(
    pivot: pd.DataFrame,
    x_title: str,
    y_title: str,
    h_boundaries: list[float] | None = None,
    description: str | None = None,
) -> None:
    z_max = int(pivot.values.max())
    fig = go.Figure(go.Heatmap(
        z=pivot.values,
        x=pivot.columns.tolist(),
        y=pivot.index.tolist(),
        colorscale=make_colorscale(z_max),
        zmin=-0.5,
        zmax=z_max + 0.5,
        text=pivot.values,
        texttemplate="%{text}",
        textfont=dict(size=12, shadow='auto'),
        showscale=True,
        colorbar=dict(tickmode='linear', tick0=0, dtick=1),
    ))
    if h_boundaries:
        n_cols = len(pivot.columns)
        for pos in h_boundaries:
            fig.add_shape(
                type='line',
                x0=-0.5, x1=n_cols - 0.5,
                y0=pos, y1=pos,
                xref='x', yref='y',
                line=dict(color='white', width=3),
            )
    fig.update_layout(
        xaxis=dict(title=x_title, side='top', tickangle=-30),
        yaxis=dict(title=y_title, autorange='reversed'),
        height=max(300, 36 * len(pivot.index) + 180),
        margin=dict(l=20, r=20, t=160, b=20),
    )
    if description:
        st.write(description)
    st.plotly_chart(fig, use_container_width=True)


# ── KDE / summary utilities ───────────────────────────────────────────────────

DIST_METRICS: list[tuple] = [
    # (field, label, transform, x_max)
    ('f1',               'F1',        None,              1.0),
    ('recall',           'Recall',    None,              1.0),
    ('precision',        'Precision', None,              1.0),
    ('duration_seconds', 'Runtime',        None,              None),
    ('total_tokens',     'Tokens (K)',     lambda v: v / 1e3, None),
]

KDE_PALETTE = ['#e74c3c', '#3498db', '#2ecc71', '#f39c12', '#9b59b6', '#1abc9c']

SUMMARY_COLUMN_CONFIG = {
    'mean_f1':        st.column_config.NumberColumn("Mean F1",        format="%.2f"),
    'mean_recall':    st.column_config.NumberColumn("Mean Recall",    format="%.2f"),
    'mean_precision': st.column_config.NumberColumn("Mean Precision", format="%.2f"),
    'mean_duration':  st.column_config.TextColumn("Mean Runtime"),
    'mean_tokens':    st.column_config.TextColumn("Mean Tokens"),
}


def hex_rgba(hex_color: str, alpha: float) -> str:
    r, g, b = int(hex_color[1:3], 16), int(hex_color[3:5], 16), int(hex_color[5:7], 16)
    return f"rgba({r},{g},{b},{alpha})"


def kde(values: np.ndarray, n_points: int = 300):
    if len(values) < 2 or np.std(values) == 0:
        x = np.array([values[0] - 1e-9, values[0], values[0] + 1e-9])
        return x, np.array([0.0, 1.0, 0.0])
    bw = 0.9 * np.std(values, ddof=1) * len(values) ** -0.2
    x = np.linspace(values.min() - 3 * bw, values.max() + 3 * bw, n_points)
    y = np.exp(-0.5 * ((x[:, None] - values[None, :]) / bw) ** 2).mean(axis=1) / (bw * np.sqrt(2 * np.pi))
    return x, y


_KDE_MAX_GROUPS = 3
_UNIFORM_BAR_COLOR = '#4c72b0'


def _runtime_y_ticks(max_val: float) -> tuple[list, list]:
    nice = [300, 600, 900, 1800, 3600, 7200, 14400, 21600]
    iv = min(nice, key=lambda i: abs(max_val / max(i, 1) - 5))
    tvs = list(range(0, math.ceil(max_val / iv) * iv + iv, iv))
    return tvs, [fmt_duration(t) for t in tvs]


def _tokens_y_ticks(max_val: float, n: int = 5) -> tuple[list, list]:
    tvs = [max_val * i / n for i in range(n + 1)]
    labels = ['0' if v == 0 else fmt_tokens(v) for v in tvs]
    return tvs, labels


def _dist_subplots(df: pd.DataFrame, group_col: str, groups: list[str], sort_bars: bool = False) -> None:
    kde_scores = len(groups) <= _KDE_MAX_GROUPS
    multi_color_bars = kde_scores  # match KDE palette only when KDEs are also shown
    n_cols = 3
    n_rows = math.ceil(len(DIST_METRICS) / n_cols)
    fig = make_subplots(
        rows=n_rows, cols=n_cols,
        subplot_titles=[m[1] for m in DIST_METRICS],
        horizontal_spacing=0.08,
        vertical_spacing=0.20,
    )

    for mi, (field, _label, transform, x_max) in enumerate(DIST_METRICS):
        row, col = mi // n_cols + 1, mi % n_cols + 1
        is_runtime = field == 'mean_duration_seconds'
        is_tokens  = field == 'mean_total_tokens'
        use_bar = (not kde_scores) or is_runtime or is_tokens

        if use_bar:
            bar_x, bar_y, bar_colors = [], [], []
            for gi, group in enumerate(groups):
                vals = df[df[group_col] == group][field].dropna().values
                if len(vals) == 0:
                    continue
                bar_x.append(group)
                bar_y.append(float(np.mean(vals)))
                bar_colors.append(KDE_PALETTE[gi % len(KDE_PALETTE)] if multi_color_bars else _UNIFORM_BAR_COLOR)

            if sort_bars and bar_y:
                bar_x, bar_y, bar_colors = zip(*sorted(zip(bar_x, bar_y, bar_colors), key=lambda t: t[1], reverse=True))

            fig.add_trace(
                go.Bar(x=bar_x, y=bar_y, marker_color=bar_colors, showlegend=False),
                row=row, col=col,
            )
            fig.update_xaxes(tickangle=-30, row=row, col=col)

            if is_runtime and bar_y:
                tvs, labels = _runtime_y_ticks(max(bar_y))
                fig.update_yaxes(tickvals=tvs, ticktext=labels, range=[0, None], row=row, col=col)
            elif is_tokens and bar_y:
                tvs, labels = _tokens_y_ticks(max(bar_y))
                fig.update_yaxes(tickvals=tvs, ticktext=labels, range=[0, None], row=row, col=col)
            else:
                fig.update_yaxes(tickformat='.2f', range=[0, x_max], row=row, col=col)

        else:
            # KDE
            for gi, group in enumerate(groups):
                raw = df[df[group_col] == group][field].dropna().values
                if len(raw) == 0:
                    continue
                dvals = transform(raw) if transform else raw.copy()
                color = KDE_PALETTE[gi % len(KDE_PALETTE)]
                x, y = kde(dvals)
                mask = x >= 0
                xc, yc = x[mask], y[mask]
                if len(xc) == 0:
                    continue
                fig.add_trace(
                    go.Scatter(
                        x=xc, y=yc,
                        mode='lines',
                        fill='tozeroy',
                        fillcolor=hex_rgba(color, 0.25),
                        line=dict(color=hex_rgba(color, 0.90), width=1.5),
                        name=group,
                        legendgroup=group,
                        showlegend=(mi == 0),
                    ),
                    row=row, col=col,
                )
            fig.update_xaxes(tickformat='.2f', range=[0, x_max], row=row, col=col)
            fig.update_yaxes(showticklabels=False, row=row, col=col)

    fig.update_layout(
        height=260 * n_rows,
        margin=dict(l=10, r=10, t=50, b=10),
        showlegend=kde_scores,
        legend=dict(orientation='h', x=0.5, y=-0.08, xanchor='center'),
        hovermode=False,
    )
    st.plotly_chart(fig, use_container_width=True)


def render_summary(df: pd.DataFrame, group_col: str, group_label: str, groups: list[str], sort_bars: bool = False) -> None:
    agg = (
        df
        .groupby(group_col, sort=False)
        .agg(
            mean_f1=('f1', 'mean'),
            mean_recall=('recall', 'mean'),
            mean_precision=('precision', 'mean'),
            mean_duration_seconds=('duration_seconds', 'mean'),
            mean_total_tokens=('total_tokens', 'mean'),
        )
        .reindex(groups)
        .reset_index()
    )
    agg['mean_duration'] = agg['mean_duration_seconds'].apply(fmt_duration)
    agg['mean_tokens']   = agg['mean_total_tokens'].apply(fmt_tokens)
    agg = agg.drop(columns=['mean_duration_seconds', 'mean_total_tokens'])
    st.dataframe(
        agg,
        use_container_width=True,
        hide_index=True,
        column_config={group_col: st.column_config.TextColumn(group_label), **SUMMARY_COLUMN_CONFIG},
    )
    _dist_subplots(df, group_col, groups, sort_bars=sort_bars)
