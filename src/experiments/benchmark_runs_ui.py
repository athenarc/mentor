"""Streamlit entry point for screening benchmark dashboards.

Configures page layout, loads aggregated run summaries from the benchmark
results directory (via CLI args after ``--``), and registers multi-page
navigation for leaderboard, coverage, data, and research-question views.
"""

import logging

from dotenv import load_dotenv

import streamlit as st
from streamlit_app.shared import get_new_runs

load_dotenv()

LOGGER = logging.getLogger(__name__)

st.set_page_config(
    page_title="Benchmark Results",
    layout="wide",
    initial_sidebar_state="expanded",
)

try:
    runs_df = get_new_runs()
    LOGGER.info(f'Loaded {len(runs_df)} runs via the new loader')
except Exception:
    LOGGER.exception('Failed to load benchmark results via the new loader')

pg = st.navigation([
    st.Page("streamlit_app/pages/home.py", title="Home", icon=":material/home:"),
    st.Page("streamlit_app/pages/leaderboard.py", title="Leaderboard", icon=":material/emoji_events:"),
    st.Page("streamlit_app/pages/coverage.py", title="Coverage", icon=":material/grid_on:"),
    st.Page("streamlit_app/pages/data.py", title="Data", icon=":material/table_chart:"),
    st.Page("streamlit_app/pages/research_questions.py", title="Research Questions", icon=":material/quiz:"),
])
pg.run()
