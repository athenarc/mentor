import pandas as pd
import streamlit as st

from streamlit_app.constants import (
    EXPERIMENT_ARCHITECTURE_VALUE_TO_LABEL_INDEX, GOLD_LABEL_POLICY_VALUE_TO_LABEL_INDEX,
)
from streamlit_app.shared import (
    SIZE_BAND_ORDER, SUMMARY_COLUMN_CONFIG,
    fmt_duration, fmt_tokens, get_new_runs, render_summary,
)

st.title("Leaderboard")

runs = get_new_runs()

with st.sidebar:
    policy_options = sorted(runs['gold_label_policy'].unique())
    selected_policy = st.selectbox(
        "Gold label policy",
        options=policy_options,
        format_func=lambda v: GOLD_LABEL_POLICY_VALUE_TO_LABEL_INDEX.get(v, v),
    )

runs = runs[runs['gold_label_policy'] == selected_policy]
scored = runs[runs['scored_for_aggregate']]


def _best_model_table(
        df: pd.DataFrame, group_col: str, group_label: str, groups: list[str], format_func=None,
) -> None:
    agg = (
        df
        .groupby([group_col, 'gatekeeper_preset'])
        .agg(
            mean_f1=('f1', 'mean'),
            mean_recall=('recall', 'mean'),
            mean_precision=('precision', 'mean'),
            mean_duration_seconds=('duration_seconds', 'mean'),
            mean_total_tokens=('total_tokens', 'mean'),
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
    if format_func:
        best[group_col] = best[group_col].map(format_func)
    best['mean_duration'] = best['mean_duration_seconds'].apply(fmt_duration)
    best['mean_tokens'] = best['mean_total_tokens'].apply(fmt_tokens)
    best = best.drop(columns=['mean_duration_seconds', 'mean_total_tokens'])
    st.dataframe(
        best,
        use_container_width=True,
        hide_index=True,
        column_config={
            group_col: st.column_config.TextColumn(group_label),
            'gatekeeper_preset': st.column_config.TextColumn("Best Model"),
            **SUMMARY_COLUMN_CONFIG,
        },
    )


# ── Overall model performance ─────────────────────────────────────────────────

st.subheader("Model Performance")

models_by_f1 = (
    scored
    .groupby('gatekeeper_preset')['f1']
    .mean()
    .sort_values(ascending=False)
    .index.tolist()
)

render_summary(scored, group_col='gatekeeper_preset', group_label='Model', groups=models_by_f1, sort_bars=True)

# ── Best model per architecture ───────────────────────────────────────────────

st.subheader("Best Model per Architecture")
_best_model_table(
    scored,
    group_col='benchmark_architecture',
    group_label='Architecture',
    groups=sorted(scored['benchmark_architecture'].unique()),
    format_func=lambda v: EXPERIMENT_ARCHITECTURE_VALUE_TO_LABEL_INDEX.get(v, v),
)

# ── Best model per size band ──────────────────────────────────────────────────

st.subheader("Best Model per Size Band")
_band_groups = [b for b in SIZE_BAND_ORDER if b in scored['size_band'].values]
_band_groups += sorted(b for b in scored['size_band'].unique() if b not in SIZE_BAND_ORDER)
_best_model_table(
    scored,
    group_col='size_band',
    group_label='Size Band',
    groups=_band_groups,
)

# ── Best model per suite ──────────────────────────────────────────────────────

st.subheader("Best Model per Suite")
_best_model_table(
    scored,
    group_col='suite',
    group_label='Suite',
    groups=sorted(scored['suite'].unique()),
)
