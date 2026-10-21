"""Benchmark dashboard landing page with links to each analysis view."""

import streamlit as st

st.title("Benchmark Results")
st.write(
    "This dashboard provides insight into the results of systematic review "
    "screening benchmarks across different architectures, models, and review datasets."
)

st.divider()

col1, col2, col3, col4 = st.columns(4, gap="large")

with col1:
    st.subheader(":material/emoji_events: Leaderboard")
    st.write(
        "Compare model performance, and see the best model "
        "per architecture, size band, and suite."
    )
    st.page_link("streamlit_app/pages/leaderboard.py", label="Go to Leaderboard")

with col2:
    st.subheader(":material/grid_on: Coverage")
    st.write(
        "Explore run coverage across reviews and suites "
        "for each architecture and model combination."
    )
    st.page_link("streamlit_app/pages/coverage.py", label="Go to Coverage")

with col3:
    st.subheader(":material/table_chart: Data")
    st.write(
        "Browse and filter the full benchmark results table "
        "with detailed metrics per run."
    )
    st.page_link("streamlit_app/pages/data.py", label="Go to Data")

with col4:
    st.subheader(":material/quiz: Research Questions")
    st.write(
        "Answer targeted research questions with focused "
        "data aggregations and visualizations."
    )
    st.page_link("streamlit_app/pages/research_questions.py", label="Go to Research Questions")
