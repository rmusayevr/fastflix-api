from app.core.search import get_search_client
from app.models.movie import Movie
from app.schemas.search import MovieSearchDoc

INDEX_NAME = "movies"


async def configure_search_index():
    """
    Sets up the index settings:
    - Searchable: Fields to match against (Title, Description).
    - Filterable: Fields to filter by (Year, Genre).
    - Sortable: Fields to sort by (Rating, Year).
    """
    client = get_search_client()
    if not client:
        return

    index = client.index(INDEX_NAME)

    index.update_filterable_attributes(["genres", "release_year", "rating"])

    index.update_sortable_attributes(["rating", "release_year"])

    print(f"✅ MeiliSearch Index '{INDEX_NAME}' configured.")


async def add_movies_to_search(movies: list[Movie]):
    """
    Transforms SQL Movie models into Search Documents and uploads them.
    """
    client = get_search_client()
    if not client:
        return

    documents = []
    for movie in movies:
        doc = MovieSearchDoc(
            id=movie.id,
            title=movie.title,
            description=movie.description,
            release_year=movie.release_year,
            rating=movie.average_rating or 0.0,
            thumbnail_url=movie.thumbnail_url,
            slug=movie.slug,
            genres=[g.name for g in movie.genres],
        )
        documents.append(doc.model_dump())

    if documents:
        task = client.index(INDEX_NAME).add_documents(documents)
        print(
            f"🚀 Sent {len(documents)} movies to search engine (Task UID: {task.task_uid})"
        )


async def search_movies_in_meili(query: str, limit: int = 10, offset: int = 0):
    """
    Searches MeiliSearch and returns a dictionary with IDs and Total count.
    """
    client = get_search_client()
    if not client:
        return {"ids": [], "total": 0}

    try:
        results = client.index(INDEX_NAME).search(
            query,
            {
                "limit": limit,
                "offset": offset,
                "attributesToRetrieve": ["id"],
            },
        )

        hits = results.get("hits", [])
        total = results.get("estimatedTotalHits", 0)

        return {"ids": [hit["id"] for hit in hits], "total": total}
    except Exception as e:
        print(f"⚠️ Search failed: {e}")
        return {"ids": [], "total": 0}


def index_movie(movie: Movie):
    """
    Adds or Updates a SINGLE movie in MeiliSearch.
    This is synchronous, intended to be run in a BackgroundTask.
    """
    client = get_search_client()
    if not client:
        return

    try:
        doc = MovieSearchDoc(
            id=movie.id,
            title=movie.title,
            description=movie.description,
            release_year=movie.release_year,
            rating=movie.average_rating or 0.0,
            thumbnail_url=movie.thumbnail_url,
            slug=movie.slug,
            genres=[g.name for g in movie.genres],
        )

        client.index(INDEX_NAME).add_documents([doc.model_dump()])
        print(f"🔄 Search Index Updated: {movie.title}")
    except Exception as e:
        print(f"⚠️ Failed to index movie {movie.id}: {e}")


def remove_movie_from_index(movie_id: int):
    """
    Removes a movie from the search index.
    """
    client = get_search_client()
    if not client:
        return

    try:
        client.index(INDEX_NAME).delete_document(str(movie_id))
        print(f"🗑️ Search Index Deleted: ID {movie_id}")
    except Exception as e:
        print(f"⚠️ Failed to remove movie {movie_id} from index: {e}")
