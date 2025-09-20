from datetime import timedelta

from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Genre(models.Model):
    tmdb_id = models.IntegerField(unique=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Movie(models.Model):
    tmdb_id = models.IntegerField(unique=True)
    title = models.CharField(max_length=255)
    overview = models.TextField(blank=True, null=True)
    poster_path = models.CharField(max_length=255, blank=True, null=True)
    genres = models.ManyToManyField(Genre)
    cached_at = models.DateTimeField(auto_now_add=True)  # last synced
    cache_ttl = models.IntegerField(default=86400)  # seconds (1 day)

    def __str__(self):
        return self.title


class TVShow(models.Model):
    tmdb_id = models.IntegerField(unique=True)
    name = models.CharField(max_length=255)
    overview = models.TextField(blank=True)
    first_air_date = models.DateField(null=True, blank=True)
    poster_path = models.CharField(max_length=255, blank=True)
    genres = models.ManyToManyField(Genre, related_name="tvshows")
    cached_at = models.DateTimeField(auto_now_add=True)  # last synced
    cache_ttl = models.IntegerField(default=86400)  # seconds (1 day)

    def __str__(self):
        return self.name


class UserFavorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="favorites")
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "movie")


class UserWatchlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="watchlist")
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "movie")


class UserReview(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reviews")
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    review_text = models.TextField()
    rating = models.IntegerField()  # e.g., 1-10
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("user", "movie")
