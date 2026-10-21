"""Research-questions page: preset analyses (e.g. deployment tier comparisons)."""

import logging

import streamlit as st

from streamlit_app.constants import (
    EXPERIMENT_ARCHITECTURE_VALUE_TO_LABEL_INDEX, GOLD_LABEL_POLICY_VALUE_TO_LABEL_INDEX, MODEL_DEPLOYMENT_TIERS,
)
from streamlit_app.shared import SIZE_BAND_ORDER, get_new_runs, render_summary

LOGGER = logging.getLogger(__name__)

st.title("Research Questions")

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

dataset_models = set(runs['gatekeeper_preset'].unique())

# Keep only tier entries that actually exist in the loaded dataset — a name in
# MODEL_DEPLOYMENT_TIERS that doesn't match a real gatekeeper_preset (e.g. a typo)
# would otherwise silently vanish from the grouping instead of being reported.
model_deployment_tiers = {
    tier: sorted(models & dataset_models) for tier, models in MODEL_DEPLOYMENT_TIERS.items()
}
missing_by_tier = {
    tier: sorted(models - dataset_models) for tier, models in MODEL_DEPLOYMENT_TIERS.items()
}
for tier, missing in missing_by_tier.items():
    if missing:
        LOGGER.warning(
            f'MODEL_DEPLOYMENT_TIERS declares model(s) for tier "{tier}" not found in the loaded '
            f'dataset: {", ".join(missing)}.'
        )

model_to_deployment_tier = {
    model: tier for tier, models in model_deployment_tiers.items() for model in models
}

# ── Performance of locally deployable models vs provided models ────────────────

tooltip = "\n\n".join(
    f"**{tier.replace('_', ' ').title()}**: {', '.join(models) if models else '—'}"
    for tier, models in model_deployment_tiers.items()
)

st.subheader("Performance of locally deployable models vs provided models", help=tooltip)

tiered = scored[scored['gatekeeper_preset'].isin(model_to_deployment_tier)].copy()
tiered['deployment_tier'] = tiered['gatekeeper_preset'].map(model_to_deployment_tier)

render_summary(
    tiered,
    group_col='deployment_tier',
    group_label='Deployment Tier',
    groups=sorted(tiered['deployment_tier'].unique()),
)

tier_columns = sorted(tiered['deployment_tier'].unique())
tier_column_labels = {t: t.replace('_', ' ').title() for t in tier_columns}
tier_column_config = {
    label: st.column_config.NumberColumn(label, format="%.2f") for label in tier_column_labels.values()
}

# ── Mean F1 — Architecture × Deployment Tier ────────────────────────────────

arch_tiered = tiered.copy()
arch_tiered['benchmark_architecture'] = arch_tiered['benchmark_architecture'].map(
    lambda v: EXPERIMENT_ARCHITECTURE_VALUE_TO_LABEL_INDEX.get(v, v)
)
arch_f1_pivot = (
    arch_tiered
    .pivot_table(index='benchmark_architecture', columns='deployment_tier', values='f1', aggfunc='mean')
    .reindex(columns=tier_columns)
    .rename(columns=tier_column_labels)
    .sort_index()
)
st.markdown("**Mean F1 — Architecture × Deployment Tier**")
st.dataframe(arch_f1_pivot, use_container_width=True, column_config=tier_column_config)

# ── Mean F1 — Size Band × Deployment Tier ───────────────────────────────────

band_order = [b for b in SIZE_BAND_ORDER if b in tiered['size_band'].values]
band_order += sorted(b for b in tiered['size_band'].unique() if b not in SIZE_BAND_ORDER)
band_f1_pivot = (
    tiered
    .pivot_table(index='size_band', columns='deployment_tier', values='f1', aggfunc='mean')
    .reindex(index=band_order, columns=tier_columns)
    .rename(columns=tier_column_labels)
)
st.markdown("**Mean F1 — Size Band × Deployment Tier**")
st.dataframe(band_f1_pivot, use_container_width=True, column_config=tier_column_config)
