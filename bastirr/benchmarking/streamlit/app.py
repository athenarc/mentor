from dotenv import load_dotenv
import streamlit as st

load_dotenv()

st.set_page_config(
    page_title="Benchmark Results",
    layout="wide",
    initial_sidebar_state="expanded",
)

pg = st.navigation([
    st.Page("pages/home.py",          title="Home",        icon=":material/home:"),
    st.Page("pages/leaderboard.py",   title="Leaderboard", icon=":material/emoji_events:"),
    st.Page("pages/coverage.py",      title="Coverage",    icon=":material/grid_on:"),
    st.Page("pages/data.py",          title="Data",        icon=":material/table_chart:"),
])
pg.run()
