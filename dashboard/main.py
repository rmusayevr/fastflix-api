import extra_streamlit_components as stx
import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import os

API_URL = os.getenv("API_URL", "http://web:8000/api/v1")

st.set_page_config(page_title="FastFlix Admin", page_icon="🎬", layout="wide")

st.title("🎬 FastFlix Admin Dashboard")

cookie_manager = stx.CookieManager()

if "access_token" not in st.session_state:
    st.session_state["access_token"] = None

cookie_token = cookie_manager.get("access_token")

if cookie_token and st.session_state["access_token"] is None:
    st.session_state["access_token"] = cookie_token


def login():
    st.sidebar.header("🔐 Login")
    username = st.sidebar.text_input("Email", value="admin@example.com")
    password = st.sidebar.text_input("Password", type="password")

    if st.sidebar.button("Login"):
        try:
            data = {"username": username, "password": password}
            res = requests.post(f"{API_URL}/auth/access-token", data=data)

            if res.status_code == 200:
                token_data = res.json()
                token = token_data["access_token"]

                cookie_manager.set("access_token", token, expires_at=None)

                st.session_state["access_token"] = token
                st.sidebar.success("Logged in!")
                st.rerun()
            else:
                st.sidebar.error("Invalid credentials")
        except Exception as e:
            st.sidebar.error(f"Connection Error: {e}")


def logout():
    if st.sidebar.button("Logout"):
        cookie_manager.delete("access_token")
        st.session_state["access_token"] = None
        st.rerun()


if not st.session_state["access_token"]:
    st.warning("Please log in via the sidebar to manage movies.")
    login()
    st.stop()

st.sidebar.success("✅ Authenticated")
logout()
headers = {"Authorization": f"Bearer {st.session_state['access_token']}"}

page = st.sidebar.radio(
    "Go to", ["Overview", "Manage Movies", "Semantic Search", "AI Chat"]
)

genre_map = {}
if page == "Manage Movies":
    g_res = requests.get(f"{API_URL}/genres/", headers=headers)
    if g_res.status_code == 200:
        genre_map = {g["name"]: g["id"] for g in g_res.json()}


if page == "Overview":
    st.header("📊 System Analytics")

    col1, col2, col3 = st.columns(3)

    try:
        res_movies = requests.get(f"{API_URL}/movies/?skip=0&limit=1")
        if res_movies.status_code == 200:
            total_count = res_movies.headers.get("x-total-count", "100+")
            col1.metric("Total Movies", total_count)
            col2.metric("Active Users", "1,240")
            col3.metric("API Uptime", "99.9%")

        st.divider()

        st.subheader("🎥 Movies by Genre")

        res_stats = requests.get(f"{API_URL}/movies/analytics/genres")

        if res_stats.status_code == 200:
            data = res_stats.json()

            if data:
                df = pd.DataFrame(data)

                fig = px.pie(
                    df,
                    names="genre",
                    values="count",
                    title="Top Genres Distribution",
                    hole=0.4,
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No genre data available yet.")
        else:
            st.warning("Could not load analytics data.")

    except Exception as e:
        st.error(f"Connection Error: {e}")

    st.info("Select 'Semantic Search' in the sidebar to test your AI!")

elif page == "Manage Movies":
    st.header("🛠️ Movie Management")
    tab1, tab2 = st.tabs(["➕ Add Movie", "🗑️ Delete Movie"])

    genre_map = {}
    try:
        g_res = requests.get(f"{API_URL}/genres/", headers=headers)
        if g_res.status_code == 200:
            genres_list = g_res.json()
            genre_map = {g["name"]: g["id"] for g in genres_list}
        else:
            st.warning("Could not load genres list.")
    except Exception as e:
        st.error(f"Failed to fetch genres: {e}")

    with tab1:
        st.subheader("Add a New Movie")
        with st.form("add_movie_form"):
            new_title = st.text_input("Title")
            new_desc = st.text_area("Description")

            col1, col2 = st.columns(2)
            with col1:
                new_year = st.number_input("Release Year", 1900, 2100, 2026)
                selected_genre_names = st.multiselect(
                    "Select Genres", options=list(genre_map.keys())
                )
            with col2:
                new_video = st.text_input(
                    "Video URL", "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
                )
                new_thumb = st.text_input(
                    "Thumbnail URL", "https://placehold.co/600x400"
                )

            submitted = st.form_submit_button("Create Movie")

            if submitted:
                if not new_title or not new_desc or not new_video:
                    st.error("Title, Description, and Video URL are required.")
                else:
                    selected_ids = [genre_map[n] for n in selected_genre_names]
                    payload = {
                        "title": new_title,
                        "description": new_desc,
                        "release_year": int(new_year),
                        "video_url": new_video,
                        "thumbnail_url": new_thumb,
                        "genre_ids": selected_ids,
                    }

                    try:
                        res = requests.post(
                            f"{API_URL}/movies/", json=payload, headers=headers
                        )
                        if res.status_code in [200, 201]:
                            st.success(f"✅ Created: {new_title}")
                        else:
                            st.error(f"Error: {res.text}")
                    except Exception as e:
                        st.error(f"Failed: {e}")

    with tab2:
        st.subheader("Delete Movie")
        st.warning("⚠️ This action cannot be undone.")

        del_id = st.number_input("Movie ID to Delete", min_value=1, step=1)

        if st.button("🗑️ Delete Movie", type="primary"):
            try:
                res = requests.delete(f"{API_URL}/movies/{del_id}", headers=headers)

                if res.status_code in [200, 204]:
                    st.success(f"✅ Movie ID {del_id} deleted successfully.")
                elif res.status_code == 404:
                    st.error("❌ Movie not found. Check the ID.")
                elif res.status_code == 403:
                    st.error("⛔ Permission denied. Are you an admin?")
                else:
                    st.error(f"❌ Error {res.status_code}: {res.text}")

            except Exception as e:
                st.error(f"Connection Failed: {e}")

elif page == "Semantic Search":
    st.header("🔍 Semantic Search")
    q = st.text_input("Query")
    if st.button("Search") and q:
        res = requests.get(f"{API_URL}/movies/semantic_search", params={"query": q})
        if res.status_code == 200:
            for m in res.json():
                st.write(f"**{m['title']}** - {m['description']}")
                st.divider()

elif page == "AI Chat":
    st.header("🤖 AI Chat")
    q = st.text_input("Question")
    if st.button("Ask") and q:
        res = requests.post(f"{API_URL}/movies/chat", params={"question": q})
        if res.status_code == 200:
            st.write(res.json().get("answer"))
