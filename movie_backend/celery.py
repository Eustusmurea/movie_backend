import os

from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "movie_backend.settings")

app = Celery("movie_backend")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks(["users.tasks", "movies.tasks"])


# Schedule periodic tasks
app.conf.beat_schedule = {
    "update-movies-every-hour": {
        "task": "movies.tasks.update_movies_from_tmdb",
        "schedule": crontab(minute=0, hour="*"),
    },
}
