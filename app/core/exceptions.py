class MovieNotFoundException(Exception):
    def __init__(self, movie_id: int):
        self.movie_id = movie_id
        self.message = f"Movie with ID {movie_id} not found."
        super().__init__(self.message)
