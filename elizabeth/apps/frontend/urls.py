from django.urls import path, re_path

from elizabeth.apps.frontend.views import FrontendAppView

urlpatterns = [
    path("", FrontendAppView.as_view(), name="frontend-app"),
    re_path(
        r"^(?P<path>.+)/?$", FrontendAppView.as_view(), name="frontend-app-catchall"
    ),
]
