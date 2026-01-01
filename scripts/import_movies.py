import requests
import time
import os
from dotenv import load_dotenv

load_dotenv()

API_URL = "http://localhost:8000/api/v1"
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")
TMDB_API_KEY = os.getenv("TMDB_API_KEY")


def get_access_token():
    print(f"🔑 Logging in as {ADMIN_EMAIL}...")
    response = requests.post(
        f"{API_URL}/auth/token",
        data={"username": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
    )
    if response.status_code != 200:
        print(f"❌ Login Failed: {response.text}")
        exit(1)
    return response.json()["access_token"]


def fetch_tmdb_movies():
    """Fetch top rated movies from TMDB."""
    print("🌍 Fetching movies from TMDB...")

    if not TMDB_API_KEY or "YOUR_TMDB" in TMDB_API_KEY:
        print("❌ ERROR: TMDB_API_KEY is missing or invalid in .env file")
        return []

    url = f"https://api.themoviedb.org/3/movie/top_rated?api_key={TMDB_API_KEY}&language=en-US&page=1"
    response = requests.get(url)

    # 👇 DEBUGGING: Print error if request fails
    if response.status_code != 200:
        print(f"❌ TMDB Error {response.status_code}: {response.text}")
        return []

    return response.json().get("results", [])


def upload_movie(movie, token):
    # ... (Keep existing upload logic) ...
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "title": movie["title"],
        "director": "Unknown",
        "description": movie["overview"],
    }

    res = requests.post(f"{API_URL}/movies/", json=payload, headers=headers)

    if res.status_code == 201:
        print(f"✅ Imported: {movie['title']}")
    elif res.status_code == 429:
        print(f"⚠️ Rate Limit Hit! Sleeping...")
        time.sleep(60)
    else:
        print(f"❌ Failed: {movie['title']} - {res.text}")


if __name__ == "__main__":
    token = get_access_token()
    movies = fetch_tmdb_movies()

    print(f"🚀 Starting import of {len(movies)} movies...")
    for movie in movies:
        upload_movie(movie, token)
        time.sleep(0.2)

    print("✨ Import Complete!")
