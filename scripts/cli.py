import asyncio
import os
import click
import httpx
from dotenv import load_dotenv

load_dotenv()

API_URL = "http://localhost:8000/api/v1"
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@gmail.com")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")
TMDB_API_KEY = os.getenv("TMDB_API_KEY")


class GenreMapper:
    """
    Handles the translation between TMDB Genre IDs and FastFlix Genre IDs.
    """

    def __init__(self, client: httpx.AsyncClient, token: str):
        self.client = client
        self.token = token
        self.tmdb_genres = {}
        self.local_genres = {}

    async def load_tmdb_genres(self):
        """Fetch the official list of genres from TMDB."""
        if not TMDB_API_KEY:
            click.secho("❌ Error: TMDB_API_KEY missing.", fg="red")
            return

        url = f"https://api.themoviedb.org/3/genre/movie/list?api_key={TMDB_API_KEY}&language=en-US"
        resp = await self.client.get(url)
        if resp.status_code == 200:
            for g in resp.json().get("genres", []):
                self.tmdb_genres[g["id"]] = g["name"]
            click.secho(
                f"📋 Loaded {len(self.tmdb_genres)} genres from TMDB.", fg="cyan"
            )
        else:
            click.secho(f"⚠️ Failed to load genres from TMDB: {resp.text}", fg="yellow")

    async def sync_with_api(self):
        """
        Ensures all TMDB genres exist in FastFlix API.
        Populates self.local_genres map.
        """
        headers = {"Authorization": f"Bearer {self.token}"}

        try:
            resp = await self.client.get(f"{API_URL}/genres/", headers=headers)
            if resp.status_code == 200:
                for g in resp.json():
                    self.local_genres[g["name"]] = g["id"]
            else:
                click.secho(
                    f"⚠️ Failed to fetch local genres: {resp.status_code}", fg="yellow"
                )
        except httpx.RequestError as e:
            click.secho(f"💥 Error connecting to API: {e}", fg="red")
            return

        for name in self.tmdb_genres.values():
            if name not in self.local_genres:
                await self._create_remote_genre(name, headers)

    async def _create_remote_genre(self, name, headers):
        """Helper to create a genre in FastFlix."""
        payload = {"name": name}
        try:
            resp = await self.client.post(
                f"{API_URL}/genres/", json=payload, headers=headers
            )
            if resp.status_code == 201:
                data = resp.json()
                self.local_genres[data["name"]] = data["id"]
                click.secho(f"   ➕ Created genre: {name}", dim=True)
            elif resp.status_code == 400:
                pass
            else:
                click.secho(f"   ❌ Failed to create genre {name}", fg="red")
        except httpx.RequestError:
            pass

    def map_ids(self, tmdb_ids: list[int]) -> list[int]:
        """
        Converts a list of TMDB IDs [28, 12] -> FastFlix IDs [5, 9]
        """
        local_ids = []
        for t_id in tmdb_ids:
            name = self.tmdb_genres.get(t_id)
            if name and name in self.local_genres:
                local_ids.append(self.local_genres[name])
        return local_ids


@click.group()
def cli():
    """FastFlix Management CLI"""
    pass


async def get_token(client: httpx.AsyncClient) -> str:
    """Authenticate as Admin and retrieve JWT."""
    try:
        response = await client.post(
            f"{API_URL}/auth/token",
            data={"username": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
        )
        response.raise_for_status()
        return response.json()["access_token"]
    except httpx.HTTPStatusError:
        click.secho("❌ Login failed! Check credentials in .env", fg="red")
        exit(1)
    except httpx.RequestError as e:
        click.secho(f"💥 API Connection Error: {e}", fg="red")
        exit(1)


async def fetch_tmdb_movies(client: httpx.AsyncClient, page: int) -> list:
    """Fetch top-rated movies from TMDB."""
    if not TMDB_API_KEY:
        click.secho("❌ Error: TMDB_API_KEY missing.", fg="red")
        return []

    url = "https://api.themoviedb.org/3/movie/top_rated"
    params = {"api_key": TMDB_API_KEY, "language": "en-US", "page": page}

    try:
        resp = await client.get(url, params=params)
        if resp.status_code != 200:
            click.secho(f"⚠️ TMDB Error: {resp.text}", fg="yellow")
            return []
        return resp.json().get("results", [])
    except httpx.RequestError as e:
        click.secho(f"💥 TMDB Connection Error: {e}", fg="red")
        return []


async def upload_movie(client, movie, token, mapper, sem):
    """
    Uploads a single movie to the API.
    """
    async with sem:
        tmdb_ids = movie.get("genre_ids", [])
        local_genre_ids = mapper.map_ids(tmdb_ids)

        release_date = movie.get("release_date", "2000-01-01") or "2000-01-01"

        payload = {
            "title": movie["title"],
            "description": movie["overview"],
            "release_year": int(release_date.split("-")[0]),
            "video_url": f"https://www.youtube.com/results?search_query={movie['title']}+trailer",
            "thumbnail_url": f"https://image.tmdb.org/t/p/w500{movie.get('poster_path')}",
            "genre_ids": local_genre_ids,
        }

        headers = {"Authorization": f"Bearer {token}"}

        try:
            resp = await client.post(
                f"{API_URL}/movies/", json=payload, headers=headers
            )

            if resp.status_code == 201:
                click.secho(f"✅ Imported: {movie['title']}", fg="green")
            elif resp.status_code == 429:
                click.secho(f"⏳ Rate Limit Hit: {movie['title']}", fg="yellow")
            else:
                click.secho(f"❌ Failed: {movie['title']} | {resp.text}", fg="red")
        except httpx.RequestError as e:
            click.secho(f"💥 Network Error: {e}", fg="red")


@cli.command()
@click.option("--pages", default=1, help="Number of TMDB pages to fetch")
@click.option("--concurrency", default=5, help="Concurrent upload limit")
def import_movies(pages, concurrency):
    """
    Async movie importer.
    Fetches from TMDB and uploads to FastFlix API concurrently.
    """

    async def run():
        async with httpx.AsyncClient(timeout=10.0) as client:
            click.secho("🔑 Authenticating...", fg="blue")
            token = await get_token(client)

            click.secho("🔄 Syncing Genres...", fg="blue")
            mapper = GenreMapper(client, token)
            await mapper.load_tmdb_genres()
            await mapper.sync_with_api()

            click.secho(f"🌍 Fetching {pages} pages from TMDB...", fg="blue")
            all_movies = []
            for page in range(1, pages + 1):
                movies = await fetch_tmdb_movies(client, page)
                all_movies.extend(movies)

            click.secho(f"🚀 Starting upload of {len(all_movies)} movies...", fg="blue")

            sem = asyncio.Semaphore(concurrency)

            tasks = [upload_movie(client, m, token, mapper, sem) for m in all_movies]

            await asyncio.gather(*tasks)

            click.secho("✨ Import Complete!", fg="green", bold=True)

    asyncio.run(run())


if __name__ == "__main__":
    cli()
