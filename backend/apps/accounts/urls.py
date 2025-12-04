from django.urls import path

from backend.apps.accounts.views import (
    CurrentUserView,
    DeleteUserView,
    LoginView,
    RegisterView,
)

urlpatterns = [
    path("register", RegisterView.as_view(), name="auth-register"),
    path("login", LoginView.as_view(), name="auth-login"),
    path("profile", CurrentUserView.as_view(), name="auth-profile"),
    path("profile/delete", DeleteUserView.as_view(), name="auth-profile-delete"),
]
