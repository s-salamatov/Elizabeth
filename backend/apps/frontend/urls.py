from django.urls import path, re_path

from backend.apps.frontend.views import FrontendAppView

urlpatterns = [
    path("", FrontendAppView.as_view(), name="frontend-app"),
    re_path(
        r"^(?!api/|admin/|static/|media/|favicon\.ico|robots\.txt)"
        r"(?P<path>(?!.*\.[a-zA-Z0-9]+$).*)/?$",
        FrontendAppView.as_view(),
        name="frontend-app-catchall",
    ),
]
