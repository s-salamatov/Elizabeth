from django.urls import path

from elizabeth.apps.frontend.views import SearchPageView

urlpatterns = [
    path("", SearchPageView.as_view(), name="frontend-search"),
]
