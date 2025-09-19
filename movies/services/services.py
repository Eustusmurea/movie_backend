from typing import Dict, List, Optional
import requests
from django.conf import settings
from functools import lru_cache
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

TMDB_API_KEY = settings.TMDB_API_KEY
TMDB_BASE_URL = "https://api.themoviedb.org/3"
MAX_RETRIES = 3
RETRY_BACKOFF = 2  # seconds


class TMDbAPIError(Exception):
    """Custom exception for TMDb API failures."""


def _make_request(endpoint: str, params: Optional[Dict] = None) -> Optional[Dict]:
    """
    Helper to call TMDb API with retries and error handling.
    Returns None on failure.
    """
    if params is None:
        params = {}
    params["api_key"] = TMDB_API_KEY
    url = f"{TMDB_BASE_URL}{endpoint}"

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                wait = RETRY_BACKOFF * attempt
                print(f"Rate limit exceeded. Retrying in {wait} seconds...")
                time.sleep(wait)
            elif 500 <= e.response.status_code < 600:
                wait = RETRY_BACKOFF * attempt
                print(f"Server error {e.response.status_code}. Retrying in {wait} seconds...")
                time.sleep(wait)
            else:
                print(f"TMDb API HTTP error: {e}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"TMDb API request failed: {e}")
            wait = RETRY_BACKOFF * attempt
            time.sleep(wait)
    print(f"Failed to fetch {endpoint} after {MAX_RETRIES} attempts.")
    return None


# ----------------------------
# Public Movie Endpoints
# ----------------------------
def get_trending_movies() -> List[Dict]:
    data = _make_request("/trending/movie/week") or {}
    return data.get("results", [])


def get_top_rated_movies() -> List[Dict]:
    data = _make_request("/movie/top_rated") or {}
    return data.get("results", [])


def get_movie_details(movie_id: int) -> Optional[Dict]:
    return _make_request(f"/movie/{movie_id}")


def get_movies(movie_ids: List[int]) -> List[Dict]:
    """Fetch multiple movies concurrently."""
    movies = []
    with ThreadPoolExecutor(max_workers=5) as executor:
        future_to_id = {executor.submit(get_movie_details, mid): mid for mid in movie_ids}
        for future in as_completed(future_to_id):
            movie = future.result()
            if movie:
                movies.append(movie)
    return movies


def search_movies(query: str) -> List[Dict]:
    data = _make_request("/search/movie", {"query": query}) or {}
    return data.get("results", [])


def get_recommendations(movie_id: int) -> List[Dict]:
    data = _make_request(f"/movie/{movie_id}/recommendations") or {}
    return data.get("results", [])


# ----------------------------
# Genres
# ----------------------------
@lru_cache(maxsize=1)
def get_genres() -> List[Dict]:
    data = _make_request("/genre/movie/list") or {}
    return data.get("genres", [])


# ----------------------------
# TV Series Endpoints
# ----------------------------
def get_trending_tv() -> List[Dict]:
    data = _make_request("/trending/tv/week") or {}
    return data.get("results", [])


def get_tv_details(tv_id: int) -> Optional[Dict]:
    return _make_request(f"/tv/{tv_id}")


def get_tvs(tv_ids: List[int]) -> List[Dict]:
    """Fetch multiple TV shows concurrently."""
    shows = []
    with ThreadPoolExecutor(max_workers=5) as executor:
        future_to_id = {executor.submit(get_tv_details, tid): tid for tid in tv_ids}
        for future in as_completed(future_to_id):
            show = future.result()
            if show:
                shows.append(show)
    return shows


def search_tv(query: str) -> List[Dict]:
    data = _make_request("/search/tv", {"query": query}) or {}
    return data.get("results", [])


def get_tv_recommendations(tv_id: int) -> List[Dict]:
    data = _make_request(f"/tv/{tv_id}/recommendations") or {}
    return data.get("results", [])


def discover_tv() -> List[Dict]:
    data = _make_request("/discover/tv") or {}
    return data.get("results", [])


def discover_movies() -> List[Dict]:
    data = _make_request("/discover/movie") or {}
    return data.get("results", [])


# ----------------------------
# User Account Endpoints
# ----------------------------
def watchlist_movies(session_id: str, account_id: str) -> List[Dict]:
    data = _make_request(
        f"/account/{account_id}/watchlist/movies", {"session_id": session_id}
    ) or {}
    return data.get("results", [])


def watchlist_tv(session_id: str, account_id: str) -> List[Dict]:
    data = _make_request(
        f"/account/{account_id}/watchlist/tv", {"session_id": session_id}
    ) or {}
    return data.get("results", [])


def favorite_movies(session_id: str, account_id: str) -> List[Dict]:
    data = _make_request(
        f"/account/{account_id}/favorite/movies", {"session_id": session_id}
    ) or {}
    return data.get("results", [])


def favorite_tv(session_id: str, account_id: str) -> List[Dict]:
    data = _make_request(
        f"/account/{account_id}/favorite/tv", {"session_id": session_id}
    ) or {}
    return data.get("results", [])


def get_account_details(session_id: str) -> Dict:
    return _make_request("/account", {"session_id": session_id}) or {}


def create_session(request_token: str) -> str:
    data = _make_request("/authentication/session/new", {"request_token": request_token}) or {}
    return data.get("session_id", "")
