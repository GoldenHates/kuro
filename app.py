import json
import requests
import streamlit as st

st.set_page_config(
    page_title="KuroArchive | Editorial Anime Discovery",
    page_icon="📼",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Editorial Styling
st.markdown(
    """
    <style>
    .stApp {
        background-color: #0c0d10;
        color: #e5e7eb;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    h1, h2, h3 {
        color: #f9fafb !important;
        font-weight: 600 !important;
        letter-spacing: -0.02em;
    }
    .archive-card {
        background: #14161d;
        border: 1px solid #232734;
        border-radius: 8px;
        padding: 20px;
        margin-bottom: 18px;
    }
    .archive-tag {
        display: inline-block;
        background: #1f2430;
        color: #9ca3af;
        border: 1px solid #2e3547;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.75rem;
        margin-right: 6px;
        margin-bottom: 6px;
    }
    .high-seas-badge {
        display: inline-block;
        background: #3b181e;
        color: #fca5a5;
        border: 1px solid #7f1d1d;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    .poster-img {
        width: 130px;
        height: 190px;
        object-fit: cover;
        border-radius: 6px;
        border: 1px solid #232734;
        flex-shrink: 0;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# State Initialization
if "watched_vault" not in st.session_state:
    st.session_state.watched_vault = set()
if "recommendations" not in st.session_state:
    st.session_state.recommendations = []
if "sync_logs" not in st.session_state:
    st.session_state.sync_logs = []


@st.cache_data(show_spinner=False, ttl=86400)
def fetch_anime_poster(title: str) -> str:
    query = """
    query ($search: String) {
      Media(search: $search, type: ANIME) {
        coverImage {
          extraLarge
          large
