from rest_framework import serializers

from movies.models import Genre, Movie, UserFavorite, UserReview, UserWatchlist


# ----------------------------
# Genre Serializer
# ----------------------------
class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ["tmdb_id", "name"]


# ----------------------------
# Movie Serializer
# ----------------------------
class MovieSerializer(serializers.ModelSerializer):
    genres = GenreSerializer(many=True, read_only=True)

    class Meta:
        model = Movie
        fields = ["tmdb_id", "title", "overview", "poster_path", "genres"]


# ----------------------------
# Favorite Serializer
# ----------------------------
class FavoriteSerializer(serializers.ModelSerializer):
    movie = MovieSerializer(read_only=True)

    class Meta:
        model = UserFavorite
        fields = ["id", "movie", "added_at"]


# ----------------------------
# Watchlist Serializer
# ----------------------------
class WatchlistSerializer(serializers.ModelSerializer):
    movie = MovieSerializer(read_only=True)

    class Meta:
        model = UserWatchlist
        fields = ["id", "movie", "added_at"]


# ----------------------------
# Review Serializer
# ----------------------------
class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    movie = MovieSerializer(read_only=True)

    class Meta:
        model = UserReview
        fields = [
            "id",
            "user",
            "movie",
            "review_text",
            "rating",
            "created_at",
            "updated_at",
        ]
