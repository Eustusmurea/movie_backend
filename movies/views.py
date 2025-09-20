from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from movies.models import UserFavorite, UserReview, UserWatchlist
from movies.serializers import (
    FavoriteSerializer,
    MovieSerializer,
    ReviewSerializer,
    TVShowSerializer,
    WatchlistSerializer,
)
from movies.services.db_utils import get_or_create_movie, get_or_create_tv
from movies.services.pagination import paginate_queryset
from movies.services.services import get_recommendations
from movies.services.services import get_recommendations as tv_recommendations
from movies.services.services import (
    get_top_rated_movies,
    get_trending_movies,
    get_trending_tv,
)
from movies.services.services import search_movies as tmdb_search_movies
from movies.services.services import search_tv as tmdb_search_tv


class MediaViewSet(viewsets.ViewSet):
    """
    Handles movies, TV shows, favorites, watchlist, and reviews.
    """

    permission_classes = [AllowAny]

    # ----------------------------
    # Helpers
    # ----------------------------
    def _get_item(self, pk, item_type):
        if item_type == "tv":
            return get_or_create_tv(pk)
        return get_or_create_movie(pk)

    def _remove_item(self, model, user, item_id: int):
        deleted, _ = model.objects.filter(user=user, movie__tmdb_id=item_id).delete()
        return deleted

    # ----------------------------
    # Public Movie Endpoints
    # ----------------------------
    @action(detail=False, methods=["get"])
    def trending_movies(self, request):
        movies_data = get_trending_movies()
        movies = [get_or_create_movie(m["id"]) for m in movies_data if m]
        return paginate_queryset(
            [m for m in movies if m], request, lambda m: MovieSerializer(m).data
        )

    @action(detail=False, methods=["get"])
    def top_rated_movies(self, request):
        movies_data = get_top_rated_movies()
        movies = [get_or_create_movie(m["id"]) for m in movies_data if m]
        return paginate_queryset(
            [m for m in movies if m], request, lambda m: MovieSerializer(m).data
        )

    @action(detail=False, methods=["get"])
    def search_movies(self, request):
        query = request.query_params.get("q")
        if not query:
            return Response(
                {"error": "Query parameter 'q' is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        movies_data = tmdb_search_movies(query)
        movies = [get_or_create_movie(m["id"]) for m in movies_data if m]
        return paginate_queryset(
            [m for m in movies if m], request, lambda m: MovieSerializer(m).data
        )

    @action(detail=True, methods=["get"])
    def retrieve_movie(self, request, pk=None):
        movie = get_or_create_movie(pk)
        if not movie:
            return Response(
                {"error": "Movie not found."}, status=status.HTTP_404_NOT_FOUND
            )
        data = MovieSerializer(movie).data
        data["genres"] = [g.name for g in movie.genres.all()]
        return Response(data)

    @action(detail=True, methods=["get"])
    def movie_recommendations(self, request, pk=None):
        movies_data = get_recommendations(pk)
        movies = [get_or_create_movie(m["id"]) for m in movies_data if m]
        return paginate_queryset(
            [m for m in movies if m], request, lambda m: MovieSerializer(m).data
        )

    # ----------------------------
    # Public TV Endpoints
    # ----------------------------
    @action(detail=False, methods=["get"])
    def trending_tv(self, request):
        tv_data = get_trending_tv()
        shows = [get_or_create_tv(tv["id"]) for tv in tv_data if tv]
        return paginate_queryset(
            [s for s in shows if s], request, lambda s: TVShowSerializer(s).data
        )

    @action(detail=False, methods=["get"])
    def search_tv(self, request):
        query = request.query_params.get("q")
        if not query:
            return Response(
                {"error": "Query parameter 'q' is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        tv_data = tmdb_search_tv(query)
        shows = [get_or_create_tv(tv["id"]) for tv in tv_data if tv]
        return paginate_queryset(
            [s for s in shows if s], request, lambda s: TVShowSerializer(s).data
        )

    @action(detail=True, methods=["get"])
    def retrieve_tv(self, request, pk=None):
        show = get_or_create_tv(pk)
        if not show:
            return Response(
                {"error": "TV show not found."}, status=status.HTTP_404_NOT_FOUND
            )
        data = TVShowSerializer(show).data
        data["genres"] = [g.name for g in show.genres.all()]
        return Response(data)

    @action(detail=True, methods=["get"])
    def tv_recommendations(self, request, pk=None):
        tv_data = tv_recommendations(pk)
        shows = [get_or_create_tv(tv["id"]) for tv in tv_data if tv]
        return paginate_queryset(
            [s for s in shows if s], request, lambda s: TVShowSerializer(s).data
        )

    # ----------------------------
    # Favorites
    # ----------------------------
    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def add_favorite(self, request, pk=None):
        user = request.user
        item_type = request.query_params.get("type", "movie")
        item = self._get_item(pk, item_type)
        if not item:
            return Response(
                {"error": f"{item_type.title()} not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        favorite, created = UserFavorite.objects.get_or_create(user=user, movie=item)
        if not created:
            return Response(
                {"detail": "Already favorited."}, status=status.HTTP_400_BAD_REQUEST
            )
        return Response(
            FavoriteSerializer(favorite).data, status=status.HTTP_201_CREATED
        )

    @action(detail=True, methods=["delete"], permission_classes=[IsAuthenticated])
    def remove_favorite(self, request, pk=None):
        if not self._remove_item(UserFavorite, request.user, int(pk)):
            return Response(
                {"detail": "Favorite not found."}, status=status.HTTP_404_NOT_FOUND
            )
        return Response({"detail": "Favorite removed"}, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def my_favorites(self, request):
        favorites = UserFavorite.objects.filter(user=request.user)
        return Response(FavoriteSerializer(favorites, many=True).data)

    # ----------------------------
    # Watchlist
    # ----------------------------
    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def add_watchlist(self, request, pk=None):
        user = request.user
        item_type = request.query_params.get("type", "movie")
        item = self._get_item(pk, item_type)
        if not item:
            return Response(
                {"error": f"{item_type.title()} not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        watchlist, created = UserWatchlist.objects.get_or_create(user=user, movie=item)
        if not created:
            return Response(
                {"detail": "Already in watchlist."}, status=status.HTTP_400_BAD_REQUEST
            )
        return Response(
            WatchlistSerializer(watchlist).data, status=status.HTTP_201_CREATED
        )

    @action(detail=True, methods=["delete"], permission_classes=[IsAuthenticated])
    def remove_watchlist(self, request, pk=None):
        if not self._remove_item(UserWatchlist, request.user, int(pk)):
            return Response(
                {"detail": "Watchlist item not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response({"detail": "Removed from watchlist"}, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def my_watchlist(self, request):
        watchlist = UserWatchlist.objects.filter(user=request.user)
        return Response(WatchlistSerializer(watchlist, many=True).data)

    # ----------------------------
    # Reviews
    # ----------------------------
    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def add_review(self, request, pk=None):
        user = request.user
        item_type = request.query_params.get("type", "movie")
        item = self._get_item(pk, item_type)
        if not item:
            return Response(
                {"error": f"{item_type.title()} not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = ReviewSerializer(data=request.data)
        if serializer.is_valid():
            review, created = UserReview.objects.update_or_create(
                user=user,
                movie=item,
                defaults={
                    "review_text": serializer.validated_data["review_text"],
                    "rating": serializer.validated_data["rating"],
                },
            )
            status_code = status.HTTP_201_CREATED if created else status.HTTP_200_OK
            return Response(ReviewSerializer(review).data, status=status_code)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["get"])
    def reviews(self, request, pk=None):
        item_type = request.query_params.get("type", "movie")
        item = self._get_item(pk, item_type)
        if not item:
            return Response(
                {"error": f"{item_type.title()} not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        reviews = UserReview.objects.filter(movie=item)
        return Response(ReviewSerializer(reviews, many=True).data)
