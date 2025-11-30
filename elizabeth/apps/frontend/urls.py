from django.urls import path

from apps.frontend.views import SearchPageView

urlpatterns = [
    path("", SearchPageView.as_view(), name="frontend-search"),
]
