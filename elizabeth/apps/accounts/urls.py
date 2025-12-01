from django.urls import path

from elizabeth.apps.accounts.views import CurrentUserView, LoginView, RegisterView

urlpatterns = [
    path("register", RegisterView.as_view(), name="auth-register"),
    path("login", LoginView.as_view(), name="auth-login"),
    path("me", CurrentUserView.as_view(), name="auth-me"), # todo: change "me" to profile
    # todo: implement url to delete user profile
]
