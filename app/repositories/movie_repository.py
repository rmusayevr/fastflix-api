from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, asc, case, nullslast, or_
from sqlalchemy.orm import aliased
from app.models.movie import MovieModel
from app.schemas.movie import MovieCreate, MovieUpdate
from app.models.rating import RatingModel


class MovieRepository:
    """
    Abstractions for database interactions.
    Wraps SQLAlchemy logic to decouple the Service layer from the ORM.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_movie(self, movie_data: MovieCreate, user_id: int) -> MovieModel:
        """
        Create a new movie in the database.
        """
        movie = MovieModel(
            **movie_data.model_dump(),
            user_id=user_id,
        )

        self.session.add(movie)
        await self.session.commit()
        await self.session.refresh(movie)
        return movie

    async def get_all_movies(
        self,
        skip: int,
        limit: int,
        sort_by: str = "id",
        order: str = "asc",
        min_rating: float = None,
        search_query: str = None,
    ):

        avg_rating = func.avg(RatingModel.score).label("average_score")
        rating_sort = case((avg_rating > 0, avg_rating), else_=None)

        query = (
            select(MovieModel, avg_rating)
            .outerjoin(RatingModel, MovieModel.id == RatingModel.movie_id)
            .group_by(MovieModel.id)
        )

        if search_query:
            search_pattern = f"%{search_query}%"
            query = query.where(
                or_(
                    MovieModel.title.ilike(search_pattern),
                    MovieModel.description.ilike(search_pattern),
                )
            )

        if min_rating is not None:
            query = query.having(avg_rating >= min_rating)

        if sort_by == "rating":
            sort_column = rating_sort
        elif sort_by == "title":
            sort_column = MovieModel.title
        else:
            sort_column = MovieModel.id

        query = query.order_by(
            nullslast(desc(sort_column))
            if order == "desc"
            else nullslast(asc(sort_column))
        )

        paginated_query = query.offset(skip).limit(limit)
        result = await self.session.execute(paginated_query)
        rows = result.all()

        movies = []
        for movie, avg_score in rows:
            movie.rating = round(avg_score, 1) if avg_score else 0.0
            movies.append(movie)

        subquery_stmt = (
            select(MovieModel.id)
            .outerjoin(RatingModel, MovieModel.id == RatingModel.movie_id)
            .group_by(MovieModel.id)
        )

        if min_rating is not None:
            subquery_stmt = subquery_stmt.having(avg_rating >= min_rating)

        if search_query:
            subquery_stmt = subquery_stmt.where(
                or_(
                    MovieModel.title.ilike(search_pattern),
                    MovieModel.description.ilike(search_pattern),
                )
            )

        subquery = subquery_stmt.subquery()
        count_query = select(func.count()).select_from(subquery)

        total = await self.session.scalar(count_query)

        return movies, total

    async def get_by_id(self, movie_id: int) -> MovieModel | None:
        """
        Get a movie by its ID.
        """
        query = select(MovieModel).where(MovieModel.id == movie_id)
        result = await self.session.execute(query)
        return result.scalars().first()

    async def update_movie(
        self, movie: MovieModel, update_data: MovieUpdate
    ) -> MovieModel:
        """
        Update a movie in the database.
        """
        update_dict = update_data.model_dump(exclude_unset=True)

        for key, value in update_dict.items():
            setattr(movie, key, value)

        await self.session.commit()
        await self.session.refresh(movie)
        return movie

    async def delete_movie(self, movie: MovieModel) -> None:
        """
        Delete a movie from the database.
        """
        await self.session.delete(movie)
        await self.session.commit()

    async def search_movies(self, query_str: str) -> list[MovieModel]:
        search_vector = func.to_tsvector(
            "english",
            func.coalesce(MovieModel.title, "")
            + " "
            + func.coalesce(MovieModel.description, ""),
        )

        search_query = func.websearch_to_tsquery("english", query_str)

        statement = select(MovieModel).where(search_vector.op("@@")(search_query))

        result = await self.session.execute(statement)
        return result.scalars().all()

    async def get_recommendations(self, movie_id: int, limit: int = 5):
        """
        Recommend movies based on 'Users who liked this also liked...'
        """
        Rating1 = aliased(RatingModel)
        Rating2 = aliased(RatingModel)

        query = (
            select(MovieModel)
            .join(Rating2, MovieModel.id == Rating2.movie_id)
            .join(Rating1, Rating1.user_id == Rating2.user_id)
            .where(
                Rating1.movie_id == movie_id,
                Rating1.score >= 8,
                Rating2.score >= 8,
                MovieModel.id != movie_id,
            )
            .group_by(MovieModel.id)
            .order_by(desc(func.count(Rating2.user_id)))
            .limit(limit)
        )

        result = await self.session.execute(query)
        return result.scalars().all()
