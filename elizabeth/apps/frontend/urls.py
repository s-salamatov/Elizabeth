from django.urls import path

from elizabeth.apps.frontend.views import FrontendAppView

urlpatterns = [
    path("", FrontendAppView.as_view(), name="frontend-app"),
]
