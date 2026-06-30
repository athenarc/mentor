import streamlit as st

st.title("Benchmark Results")
st.write(
    "This dashboard provides insight into the results of systematic review "
    "screening benchmarks across different architectures, models, and review datasets."
)

st.divider()

col1, col2, col3 = st.columns(3, gap="large")

with col1:
    st.subheader(":material/emoji_events: Leaderboard")
    st.write(
        "Compare model performance, and see the best model "
        "per architecture, size band, and suite."
    )
    st.page_link("pages/leaderboard.py", label="Go to Leaderboard")

with col2:
    st.subheader(":material/grid_on: Coverage")
    st.write(
        "Explore run coverage across reviews and suites "
        "for each architecture and model combination."
    )
    st.page_link("pages/coverage.py", label="Go to Coverage")

with col3:
    st.subheader(":material/table_chart: Data")
    st.write(
        "Browse and filter the full benchmark results table "
        "with detailed metrics per run."
    )
    st.page_link("pages/data.py", label="Go to Data")
