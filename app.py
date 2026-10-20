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


# Tracker Sync Functions
def sync_anilist(username: str) -> int:
    query = """
    query ($userName: String) {
      MediaListCollection(userName: $userName, type: ANIME) {
        lists {
          entries {
            media {
              title {
                romaji
                english
              }
            }
          }
        }
      }
    }
    """
    try:
        response = requests.post(
            "https://graphql.anilist.co",
            json={"query": query, "variables": {"userName": username}},
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            timeout=10,
        )
        if response.status_code == 200:
            data = response.json()
            lists = (
                data.get("data", {})
                .get("MediaListCollection", {})
                .get("lists", [])
            )
            count = 0
            for lst in lists:
                for entry in lst.get("entries", []):
                    titles = entry.get("media", {}).get("title", {})
                    if titles.get("romaji"):
                        st.session_state.watched_vault.add(
                            titles["romaji"].strip().lower()
                        )
                        count += 1
                    if titles.get("english"):
                        st.session_state.watched_vault.add(
                            titles["english"].strip().lower()
                        )
            return count
    except Exception as e:
        st.sidebar.error(f"AniList error: {e}")
    return 0


def sync_mal(username: str) -> int:
    try:
        url = f"https://api.jikan.moe/v4/users/{username}/animelist/completed"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            entries = response.json().get("data", [])
            count = 0
            for item in entries:
                anime = item.get("entry", {})
                title = anime.get("title")
                if title:
                    st.session_state.watched_vault.add(title.strip().lower())
                    count += 1
            return count
    except Exception as e:
        st.sidebar.error(f"MyAnimeList error: {e}")
    return 0


def sync_kitsu(username: str) -> int:
    try:
        user_res = requests.get(
            f"https://kitsu.io/api/edge/users?filter[name]={username}",
            headers={"Accept": "application/vnd.api+json"},
            timeout=10,
        )
        if user_res.status_code == 200:
            users = user_
