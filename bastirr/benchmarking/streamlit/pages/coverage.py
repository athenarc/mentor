import pandas as pd
import streamlit as st

from loader import DataDirectoryError
from shared import get_runs, render_heatmap

st.title("Coverage")

try:
    runs = get_runs()
except DataDirectoryError as e:
    st.error(str(e))
    st.stop()

all_presets = sorted(runs['gatekeeper_preset'].unique())
all_archs   = sorted(runs['benchmark_architecture'].unique())

review_suite_map = (
    runs[['review_key', 'suite']]
    .drop_duplicates(subset='review_key', keep='first')
    .set_index('review_key')['suite']
)
all_reviews_ordered = sorted(
    runs['review_key'].unique(),
    key=lambda r: (review_suite_map.get(r, ''), r),
)
all_review_labels = [f"{review_suite_map.get(r, '?')}/{r}" for r in all_reviews_ordered]

with st.sidebar:
    selected_arch = st.selectbox("Architecture", options=all_archs)
    st.caption(
        f"Showing coverage for **{selected_arch}**. "
        "Each cell is the total number of scored runs for that review and model combination."
    )

arch_data = runs[runs['benchmark_architecture'] == selected_arch]

# ── Review × Model ────────────────────────────────────────────────────────────

st.subheader("Review × Model")

pivot_review = (
    arch_data
    .groupby(['review_key', 'gatekeeper_preset'])['n_scored_runs']
    .sum()
    .reset_index()
    .pivot(index='review_key', columns='gatekeeper_preset', values='n_scored_runs')
    .reindex(index=all_reviews_ordered, columns=all_presets)
    .fillna(0)
    .astype(int)
)
pivot_review.index = all_review_labels
pivot_review.columns.name = None
pivot_review.index.name = None

suite_boundaries: list[float] = []
for i in range(1, len(all_reviews_ordered)):
    if review_suite_map.get(all_reviews_ordered[i]) != review_suite_map.get(all_reviews_ordered[i - 1]):
        suite_boundaries.append(i - 0.5)

render_heatmap(
    pivot_review,
    x_title="Model",
    y_title="Suite/Review",
    h_boundaries=suite_boundaries,
)
