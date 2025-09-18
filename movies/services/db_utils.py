from movies.models import Genre, Movie
from movies.services.services import get_movie_details


def get_or_create_movie(tmdb_id: int) -> Movie | None:
    """
    Returns a local Movie instance. Fetches from TMDb if not cached.
    """
    try:
        movie = Movie.objects.get(tmdb_id=tmdb_id)
        from datetime import datetime, timezone

        if movie.cached_at + movie.cache_ttl < datetime.now(timezone.utc):
            movie_data = get_movie_details(tmdb_id)
            if movie_data:
                movie.title = movie_data.get("title", movie.title)
                movie.overview = movie_data.get("overview", movie.overview)
                movie.poster_path = movie_data.get("poster_path", movie.poster_path)
                movie.save()
                _update_movie_genres(movie, movie_data.get("genres", []))
        return movie
    except Movie.DoesNotExist:
        movie_data = get_movie_details(tmdb_id)
        if not movie_data:
            return None
        movie = Movie.objects.create(
            tmdb_id=tmdb_id,
            title=movie_data.get("title", "Untitled"),
            overview=movie_data.get("overview"),
            poster_path=movie_data.get("poster_path"),
        )
        _update_movie_genres(movie, movie_data.get("genres", []))
        return movie


def _update_movie_genres(movie: Movie, genres: list[dict]):
    """
    Create genres if not exists and associate with the movie.
    """
    genre_objs = []
    for g in genres:
        genre, _ = Genre.objects.get_or_create(
            tmdb_id=g["id"], defaults={"name": g["name"]}
        )
        genre_objs.append(genre)
    if genre_objs:
        movie.genres.set(genre_objs)
