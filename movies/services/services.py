import requests
from django.conf import settings

TMDB_API_KEY = settings.TMDB_API_KEY
TMDB_BASE_URL = "https://api.themoviedb.org/3"


def _make_request(endpoint: str, params: dict = None):
    """
    Helper to call TMDb API with error handling
    """
    if params is None:
        params = {}
    params["api_key"] = TMDB_API_KEY

    url = f"{TMDB_BASE_URL}{endpoint}"
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        # Log error instead of crashing
        print(f"TMDb API error: {e}")
        return {}


def get_trending_movies():
    data = _make_request("/trending/movie/week")
    return data.get("results", [])


def get_movie_details(movie_id: int):
    return _make_request(f"/movie/{movie_id}")


def get_movies(movie_ids: list[int]):
    movies = []
    for movie_id in movie_ids:
        movie = get_movie_details(movie_id)
        if movie:
            movies.append(movie)
    return movies


def search_movies(query: str):
    data = _make_request("/search/movie", {"query": query})
    return data.get("results", [])


def get_top_rated_movies():
    data = _make_request("/movie/top_rated")
    return data.get("results", [])


def get_recommendations(movie_id: int):
    data = _make_request(f"/movie/{movie_id}/recommendations")
    return data.get("results", [])


def get_genres():
    data = _make_request("/genre/movie/list")
    return data.get("genres", [])


# tv series


def get_trending_tv():
    data = _make_request("/trending/tv/week")
    return data.get("results", [])


def discover_tv():
    data = _make_request("/discover/tv")
    return data.get("results", [])


def discover_movies():
    data = _make_request("/discover/movie")
    return data.get("results", [])


def watchlist_movies():
    data = _make_request("/watchlist/movies")
    return data.get("results", [])


def watchlist_tv():
    data = _make_request("/watchlist/tv")
    return data.get("results", [])


def favorite_movies():
    data = _make_request("/favorite/movies")
    return data.get("results", [])


def favorite_tv():
    data = _make_request("/favorite/tv")
    return data.get("results", [])


# user account details
def get_account_details():
    data = _make_request("/account", {"session_id": settings.TMDB_READ})
    return data


# create session
def create_session(request_token: str):
    data = _make_request(
        "/authentication/session/new", {"request_token": request_token}
    )
    return data.get("session_id", "")
