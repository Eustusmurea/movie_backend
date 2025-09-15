from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    """
    Custom user model extending abstract user
    Adds available to save favourite models
    """
    favourites = models.ManyToManyField("movies.Movie", blank=True, related_name="favourited_by")

    def __str__(self):
        return self.username

