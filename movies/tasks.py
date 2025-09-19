from celery import shared_task

from movies.models import Genre, Movie
from movies.services.services import get_genres, get_trending_movies


@shared_task
def update_movies_from_tmdb():
    # Update genres
    genres_data = get_genres()
    for genre_data in genres_data:
        Genre.objects.update_or_create(
            tmdb_id=genre_data["id"], defaults={"name": genre_data["name"]}
        )

    # Update trending movies
    movies_data = get_trending_movies()
    for movie_data in movies_data:
        genres = Genre.objects.filter(tmdb_id__in=movie_data["genre_ids"])
        movie, created = Movie.objects.update_or_create(
            tmdb_id=movie_data["id"],
            defaults={
                "title": movie_data["title"],
                "overview": movie_data.get("overview", ""),
                "poster_path": movie_data.get("poster_path", ""),
            },
        )
        movie.genres.set(genres)

    return {
        "status": f"Updated {len(movies_data)} movies and {len(genres_data)} genres"
    }
