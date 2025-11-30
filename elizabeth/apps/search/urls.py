from django.urls import path

from apps.search.views import BulkSearchView, SearchView

urlpatterns = [
    path("", SearchView.as_view(), name="search"),
    path("bulk", BulkSearchView.as_view(), name="search-bulk"),
]
