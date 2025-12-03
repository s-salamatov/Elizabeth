from django.urls import path, re_path

from backend.apps.frontend.views import FrontendAppView

# todo: At this moment all exceptions urls will be also captured.
# Consider migrating frontend to "/app/" path.
urlpatterns = [
    path("", FrontendAppView.as_view(), name="frontend-app"),
    re_path(
        r"^(?P<path>.+)/?$", FrontendAppView.as_view(), name="frontend-app-catchall"
    ),
]
