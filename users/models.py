from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom user model extending abstract user
    Adds available to save favourite models
    """

    username = models.CharField(max_length=150, blank=True, unique=True)
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]
    favourites = models.ManyToManyField(
        "movies.Movie", blank=True, related_name="favourited_by"
    )

    def __str__(self):
        return self.username


class UserProfile(models.Model):
    user = models.OneToOneField(
        "User", on_delete=models.CASCADE, related_name="profile"
    )
    bio = models.TextField(blank=True)
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    welcome_email_sent = models.BooleanField(default=False)

    def __str__(self):
        return f"Profile for {self.user.email}"
