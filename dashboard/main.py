import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import os

API_URL = os.getenv("API_URL", "http://web:8000/api/v1")

st.set_page_config(page_title="FastFlix Admin", page_icon="🎬", layout="wide")

st.title("🎬 FastFlix Admin Dashboard")

st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Overview", "Semantic Search", "AI Chat"])


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

elif page == "Semantic Search":
    st.header("🔍 Semantic Search Playground")
    st.caption("Test your vector database logic here.")

    query = st.text_input(
        "Search for a concept (e.g., 'lonely robot', 'time travel paradox'):"
    )

    if st.button("Search"):
        if query:
            with st.spinner("Asking the AI..."):
                try:
                    res = requests.get(
                        f"{API_URL}/movies/semantic_search", params={"query": query}
                    )

                    if res.status_code == 200:
                        movies = res.json()
                        if not movies:
                            st.warning("No matches found.")

                        for movie in movies:
                            col1, col2 = st.columns([1, 4])
                            with col1:
                                if movie.get("thumbnail_url"):
                                    st.image(movie["thumbnail_url"], width=120)
                                else:
                                    st.write("🎬 No Image")
                            with col2:
                                st.subheader(movie["title"])
                                st.write(movie["description"])
                                st.caption(
                                    f"ID: {movie['id']} | Rating: {movie['average_rating']} ⭐"
                                )
                            st.divider()
                    else:
                        st.error("Error fetching results.")
                except Exception as e:
                    st.error(f"Connection Error: {e}")

elif page == "AI Chat":
    st.header("🤖 RAG Chatbot")
    st.write("Ask questions about your movie database.")

    user_q = st.text_input("Your Question:", "Who is the villain in the robot movie?")

    if st.button("Ask AI"):
        with st.spinner("Thinking..."):
            try:
                res = requests.post(
                    f"{API_URL}/movies/chat", params={"question": user_q}
                )
                if res.status_code == 200:
                    data = res.json()
                    st.success("Answer Generated!")
                    st.markdown(f"**Answer:** {data['answer']}")

                    with st.expander("See Source Context"):
                        st.write(f"**Source Movie:** {data['source_movie']}")
                else:
                    st.error(f"API Error: {res.text}")
            except Exception as e:
                st.error(f"Connection Error: {e}")
