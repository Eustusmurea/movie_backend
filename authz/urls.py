from django.urls import path

from . import views

app_name = "authz"

urlpatterns = [
    path("register/", views.RegisterView.as_view(), name="register"),
    path("login/", views.LoginView.as_view(), name="login"),
    path("logout/", views.LogoutView.as_view(), name="logout"),
    path("user/", views.UserDetailView.as_view(), name="user_detail"),
    path("user/me/", views.CurrentUserView.as_view(), name="current_user"),
    path("user/update/", views.UserUpdateView.as_view(), name="user_update"),
    path("user/delete/", views.UserDeleteView.as_view(), name="user_delete"),
]
