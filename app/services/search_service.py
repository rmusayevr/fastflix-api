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
