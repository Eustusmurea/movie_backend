from rest_framework.routers import DefaultRouter

from .views import MovieViewSet

app_name = "movies"

router = DefaultRouter()
router.register(r"movies", MovieViewSet, basename="movies")

urlpatterns = router.urls
