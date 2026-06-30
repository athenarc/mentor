import math

import streamlit as st

from loader import DataDirectoryError
from shared import (
    DISPLAY_COLS, DURATION_STEP, SIZE_BAND_ORDER,
    between_or_nan, fmt_duration, fmt_tokens, get_runs, parse_duration,
    render_summary,
)


st.title("Data")

try:
    runs = get_runs()
except DataDirectoryError as e:
    st.error(str(e))
    st.stop()

tok_vals = runs['mean_total_tokens'].dropna()

dur_max_secs = math.ceil(runs['mean_duration_seconds'].max())
tick_secs = list(range(0, dur_max_secs, DURATION_STEP))
if not tick_secs or tick_secs[-1] < dur_max_secs:
    tick_secs.append(dur_max_secs)
tick_labels = [fmt_duration(s) for s in tick_secs]

# ── Sidebar filters ───────────────────────────────────────────────────────────

with st.sidebar:
    st.header("Filters")

    arch_filter = st.multiselect(
        "Architecture",
        options=sorted(runs['benchmark_architecture'].unique()),
    )
    policy_filter = st.multiselect(
        "Gold label policy",
        options=sorted(runs['gold_label_policy'].unique()),
    )
    suite_filter = st.multiselect(
        "Suite",
        options=sorted(runs['suite'].unique()),
    )
    review_filter = st.multiselect(
        "Review key",
        options=sorted(runs['review_key'].unique()),
    )

    ordered_bands = [b for b in SIZE_BAND_ORDER if b in runs['size_band'].values]
    ordered_bands += sorted(b for b in runs['size_band'].unique() if b not in SIZE_BAND_ORDER)
    band_filter = st.multiselect("Size band", options=ordered_bands)

    gk_filter = st.multiselect(
        "Gatekeeper preset",
        options=sorted(runs['gatekeeper_preset'].unique()),
    )

    st.divider()

    n_max = int(runs['n_studies'].max())
    n_studies_range = st.slider("N studies", 0, n_max, (0, n_max))

    balance_range = st.slider("Balance (%)", 0, 100, (0, 100))

    st.divider()

    acc_range  = st.slider("Mean accuracy",  0.0, 1.0, (0.0, 1.0), step=0.01)
    prec_range = st.slider("Mean precision", 0.0, 1.0, (0.0, 1.0), step=0.01)
    rec_range  = st.slider("Mean recall",    0.0, 1.0, (0.0, 1.0), step=0.01)
    f1_range   = st.slider("Mean F1",        0.0, 1.0, (0.0, 1.0), step=0.01)

    if not tok_vals.empty:
        tok_max = math.ceil(tok_vals.max())
        tok_range = st.slider("Mean total tokens", 0, tok_max, (0, tok_max))

    dur_range = st.select_slider(
        "Duration (HH:MM:SS)",
        options=tick_labels,
        value=(tick_labels[0], tick_labels[-1]),
    )

# ── Apply filters ─────────────────────────────────────────────────────────────

filtered = runs.copy()

if arch_filter:
    filtered = filtered[filtered['benchmark_architecture'].isin(arch_filter)]
if policy_filter:
    filtered = filtered[filtered['gold_label_policy'].isin(policy_filter)]
if suite_filter:
    filtered = filtered[filtered['suite'].isin(suite_filter)]
if review_filter:
    filtered = filtered[filtered['review_key'].isin(review_filter)]
if band_filter:
    filtered = filtered[filtered['size_band'].isin(band_filter)]
if gk_filter:
    filtered = filtered[filtered['gatekeeper_preset'].isin(gk_filter)]

filtered = filtered[filtered['n_studies'].between(n_studies_range[0], n_studies_range[1])]
filtered = filtered[filtered['balance'].between(balance_range[0] / 100, balance_range[1] / 100)]
filtered = filtered[between_or_nan(filtered['mean_accuracy'],  *acc_range)]
filtered = filtered[between_or_nan(filtered['mean_precision'], *prec_range)]
filtered = filtered[between_or_nan(filtered['mean_recall'],    *rec_range)]
filtered = filtered[between_or_nan(filtered['mean_f1'],        *f1_range)]

if not tok_vals.empty:
    filtered = filtered[between_or_nan(filtered['mean_total_tokens'], tok_range[0], tok_range[1])]

dur_start, dur_end = parse_duration(dur_range[0]), parse_duration(dur_range[1])
filtered = filtered[filtered['mean_duration_seconds'].between(dur_start, dur_end)]

# ── Full table ────────────────────────────────────────────────────────────────

st.write(f"Showing **{len(filtered)}** of **{len(runs)}** rows")

display_df = filtered[DISPLAY_COLS].copy()
display_df['balance'] = (display_df['balance'] * 100).round(2)
display_df['mean_duration'] = display_df['mean_duration_seconds'].apply(fmt_duration)
display_df = display_df.drop(columns=['mean_duration_seconds'])

st.dataframe(
    display_df,
    use_container_width=True,
    column_config={
        'benchmark_architecture': st.column_config.TextColumn("Architecture"),
        'gold_label_policy':      st.column_config.TextColumn("Gold label policy"),
        'suite':                  st.column_config.TextColumn("Suite"),
        'review_key':             st.column_config.TextColumn("Review key"),
        'size_band':              st.column_config.TextColumn("Size band"),
        'gatekeeper_preset':      st.column_config.TextColumn("Gatekeeper preset"),
        'n_runs':                 st.column_config.NumberColumn("Runs",       format="%d"),
        'n_scored_runs':          st.column_config.NumberColumn("Scored",     format="%d"),
        'n_completed_runs':       st.column_config.NumberColumn("Completed",  format="%d"),
        'n_incomplete_runs':      st.column_config.NumberColumn("Incomplete", format="%d"),
        'n_error_runs':           st.column_config.NumberColumn("Errors",     format="%d"),
        'n_studies':              st.column_config.NumberColumn("N studies",  format="%d"),
        'gold_pass_count':        st.column_config.NumberColumn("Gold pass",  format="%d"),
        'balance':                st.column_config.NumberColumn("Balance (%)", format="%.2f%%"),
        'mean_accuracy':          st.column_config.NumberColumn("Accuracy",   format="%.2f"),
        'mean_precision':         st.column_config.NumberColumn("Precision",  format="%.2f"),
        'mean_recall':            st.column_config.NumberColumn("Recall",     format="%.2f"),
        'mean_f1':                st.column_config.NumberColumn("F1",         format="%.2f"),
        'mean_total_tokens':      st.column_config.NumberColumn("Total tokens", format="%.0f"),
        'mean_duration':          st.column_config.TextColumn("Duration"),
    },
)

# ── Summary by architecture ───────────────────────────────────────────────────

st.subheader("Summary by Architecture")
render_summary(
    filtered,
    group_col='benchmark_architecture',
    group_label='Architecture',
    groups=sorted(filtered['benchmark_architecture'].unique()),
)

# ── Summary by size band ──────────────────────────────────────────────────────

st.subheader("Summary by Size Band")
_band_groups = [b for b in SIZE_BAND_ORDER if b in filtered['size_band'].values]
_band_groups += sorted(b for b in filtered['size_band'].unique() if b not in SIZE_BAND_ORDER)
render_summary(
    filtered,
    group_col='size_band',
    group_label='Size Band',
    groups=_band_groups,
)
