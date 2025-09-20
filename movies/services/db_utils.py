import logging
from datetime import datetime, timedelta, timezone
from typing import Optional

from movies.models import Genre, Movie, TVShow
from movies.services.services import get_movie_details, get_tv_details

logger = logging.getLogger(__name__)


def get_or_create_movie(tmdb_id: int) -> Optional[Movie]:
    """
    Returns a local Movie instance. Fetches from TMDb if not cached.
    """
    try:
        movie = Movie.objects.get(tmdb_id=tmdb_id)
        if (
            movie.cached_at
            and movie.cache_ttl
            and movie.cached_at + timedelta(seconds=movie.cache_ttl)
            < datetime.now(timezone.utc)
        ):
            movie_data = get_movie_details(tmdb_id)
            if movie_data:
                if movie_data.get("title"):
                    movie.title = movie_data["title"]
                if movie_data.get("overview"):
                    movie.overview = movie_data["overview"]
                if movie_data.get("poster_path"):
                    movie.poster_path = movie_data["poster_path"]
                movie.save()
                _update_movie_genres(movie, movie_data.get("genres", []))
        return movie
    except Movie.DoesNotExist:
        movie_data = get_movie_details(tmdb_id)
        if not movie_data:
            logger.warning(f"Movie {tmdb_id} not found in TMDb.")
            return None
        movie = Movie.objects.create(
            tmdb_id=tmdb_id,
            title=movie_data.get("title") or "Untitled",
            overview=movie_data.get("overview") or "",
            poster_path=movie_data.get("poster_path"),
        )
        _update_movie_genres(movie, movie_data.get("genres", []))
        return movie


def get_or_create_tv(tmdb_id: int) -> Optional[TVShow]:
    """
    Returns a local TVShow instance. Fetches from TMDb if not cached.
    """
    try:
        show = TVShow.objects.get(tmdb_id=tmdb_id)
        if (
            hasattr(show, "cached_at")
            and hasattr(show, "cache_ttl")
            and show.cached_at
            and show.cache_ttl
            and show.cached_at + timedelta(seconds=show.cache_ttl)
            < datetime.now(timezone.utc)
        ):
            show_data = get_tv_details(tmdb_id)
            if show_data:
                if show_data.get("name"):
                    show.name = show_data["name"]
                if show_data.get("overview"):
                    show.overview = show_data["overview"]
                if show_data.get("poster_path"):
                    show.poster_path = show_data["poster_path"]
                if show_data.get("first_air_date"):
                    show.first_air_date = show_data["first_air_date"]
                show.save()
                _update_tv_genres(show, show_data.get("genres", []))
        return show
    except TVShow.DoesNotExist:
        show_data = get_tv_details(tmdb_id)
        if not show_data:
            logger.warning(f"TV Show {tmdb_id} not found in TMDb.")
            return None
        show = TVShow.objects.create(
            tmdb_id=tmdb_id,
            name=show_data.get("name") or "Untitled",
            overview=show_data.get("overview") or "",
            poster_path=show_data.get("poster_path"),
            first_air_date=show_data.get("first_air_date"),
        )
        _update_tv_genres(show, show_data.get("genres", []))
        return show


def _update_movie_genres(movie: Movie, genres: list[dict]):
    genre_objs = []
    for g in genres:
        genre, _ = Genre.objects.get_or_create(
            tmdb_id=g["id"], defaults={"name": g["name"]}
        )
        genre_objs.append(genre)
    if genre_objs:
        movie.genres.set(genre_objs)


def _update_tv_genres(show: TVShow, genres: list[dict]):
    genre_objs = []
    for g in genres:
        genre, _ = Genre.objects.get_or_create(
            tmdb_id=g["id"], defaults={"name": g["name"]}
        )
        genre_objs.append(genre)
    if genre_objs:
        show.genres.set(genre_objs)
