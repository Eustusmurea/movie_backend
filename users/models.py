from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    """
    Custom user model extending abstract user
    Adds available to save favourite models
    """
    username = models.CharField(max_length=150,blank=True, unique=True)
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    favourites = models.ManyToManyField("movies.Movie", blank=True, related_name="favourited_by")

    def __str__(self):
        return self.username

