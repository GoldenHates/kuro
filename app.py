import json
import requests
import streamlit as st

st.set_page_config(page_title="KuroArchive | Editorial Anime Discovery", page_icon="📼", layout="wide")

st.markdown("""
<style>
.stApp { background-color: #0c0d10; color: #e5e7eb; font-family: sans-serif; }
h1, h2, h3 { color: #f9fafb !important; font-weight: 600 !important; letter-spacing: -0.02em; }
.archive-card { background: #14161d; border: 1px solid #232734; border-radius: 8px; padding: 20px; margin-bottom: 20px; }
.archive-tag { display: inline-block; background: #1f2430; color: #9ca3af; border: 1px solid #2e3547; padding: 2px 8px; border-radius: 4px; font-size: 0.75rem; margin-right: 6px; }
.high-seas-badge { display: inline-block; background: #3b181e; color: #fca5a5; border: 1px solid #7f1d1d; padding: 2px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: 600; }
.poster-img { width: 100%; border-radius: 6px; border: 1px solid #232734; object-fit: cover; }
</style>
""", unsafe_allow_html=True)

if "watched_vault" not in st.session_state:
    st.session_state.watched_vault = set()
if "recommendations" not in st.session_state:
    st.session_state.recommendations = []

@st.cache_data(show_spinner=False, ttl=86400)
def fetch_anime_poster(title: str) -> str:
    q = "query ($s: String) { Media(search:$s, type: ANIME) { coverImage { extraLarge large } } }"
    try:
        r = requests.post("https://graphql.anilist.co", json={"query": q, "variables": {"s": title}}, timeout=8)
        if r.status_code == 200:
            img = r.json().get("data", {}).get("Media", {}).get("coverImage", {})
            return img.get("extraLarge") or img.get("large") or ""
    except Exception:
        pass
    return "https://images.unsplash.com/photo-1578632767115-351597cf2477?w=600&auto=format&fit=crop&q=80"

def sync_anilist(username: str) -> int:
    q = "query ($u: String) { MediaListCollection(userName:$u, type: ANIME) { lists { entries { media { title { romaji english } } } } } }"
    try:
        r = requests.post("https://graphql.anilist.co", json={"query": q, "variables": {"u": username}}, timeout=10)
        if r.status_code == 200:
            lists = r.json().get("data", {}).get("MediaListCollection", {}).get("lists", [])
            count = 0
            for lst in lists:
                for entry in lst.get("entries", []):
                    t = entry.get("media", {}).get("title", {})
                    if t.get("romaji"):
                        st.session_state.watched_vault.add(t["romaji"].strip().lower())
                        count += 1
                    if t.get("english"):
                        st.session_state.watched_vault.add(t["english"].strip().lower())
            return count
    except Exception as e:
        st.sidebar.error(f"AniList error: {e}")
    return 0

def sync_mal(username: str) -> int:
    try:
        r = requests.get(f"https://api.jikan.moe/v4/users/{username}/animelist/completed", timeout=20)
        if r.status_code == 200:
            entries = r.json().get("data", [])
            for item in entries:
                title = item.get("entry", {}).get("title")
                if title:
                    st.session_state.watched_vault.add(title.strip().lower())
            return len(entries)
    except Exception as e:
        st.sidebar.error(f"MAL error: {e}")
    return 0

def sync_kitsu(username: str) -> int:
    try:
        hdrs = {"Accept": "application/vnd.api+json"}
        ur = requests.get(f"
