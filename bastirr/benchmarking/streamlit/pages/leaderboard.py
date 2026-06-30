import streamlit as st

from loader import DataDirectoryError
from shared import (
    SIZE_BAND_ORDER, SUMMARY_COLUMN_CONFIG,
    fmt_duration, fmt_tokens, get_runs, render_summary,
)

st.title("Leaderboard")

try:
    runs = get_runs()
except DataDirectoryError as e:
    st.error(str(e))
    st.stop()


def _best_model_table(group_col: str, group_label: str, groups: list[str]) -> None:
    agg = (
        runs
        .groupby([group_col, 'gatekeeper_preset'])
        .agg(
            mean_f1=('mean_f1', 'mean'),
            mean_recall=('mean_recall', 'mean'),
            mean_precision=('mean_precision', 'mean'),
            mean_duration_seconds=('mean_duration_seconds', 'mean'),
            mean_total_tokens=('mean_total_tokens', 'mean'),
        )
        .reset_index()
    )
    best = (
        agg
        .loc[agg.groupby(group_col)['mean_f1'].idxmax()]
        .set_index(group_col)
        .reindex(groups)
        .reset_index()
    )
    best['mean_duration'] = best['mean_duration_seconds'].apply(fmt_duration)
    best['mean_tokens']   = best['mean_total_tokens'].apply(fmt_tokens)
    best = best.drop(columns=['mean_duration_seconds', 'mean_total_tokens'])
    st.dataframe(
        best,
        use_container_width=True,
        hide_index=True,
        column_config={
            group_col:           st.column_config.TextColumn(group_label),
            'gatekeeper_preset': st.column_config.TextColumn("Best Model"),
            **SUMMARY_COLUMN_CONFIG,
        },
    )


# ── Overall model performance ─────────────────────────────────────────────────

st.subheader("Model Performance")

models_by_f1 = (
    runs
    .groupby('gatekeeper_preset')['mean_f1']
    .mean()
    .sort_values(ascending=False)
    .index.tolist()
)

render_summary(runs, group_col='gatekeeper_preset', group_label='Model', groups=models_by_f1, sort_bars=True)

# ── Best model per architecture ───────────────────────────────────────────────

st.subheader("Best Model per Architecture")
_best_model_table(
    group_col='benchmark_architecture',
    group_label='Architecture',
    groups=sorted(runs['benchmark_architecture'].unique()),
)

# ── Best model per size band ──────────────────────────────────────────────────

st.subheader("Best Model per Size Band")
_band_groups = [b for b in SIZE_BAND_ORDER if b in runs['size_band'].values]
_band_groups += sorted(b for b in runs['size_band'].unique() if b not in SIZE_BAND_ORDER)
_best_model_table(
    group_col='size_band',
    group_label='Size Band',
    groups=_band_groups,
)

# ── Best model per suite ──────────────────────────────────────────────────────

st.subheader("Best Model per Suite")
_best_model_table(
    group_col='suite',
    group_label='Suite',
    groups=sorted(runs['suite'].unique()),
)
